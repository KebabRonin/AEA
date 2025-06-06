use crate::{
    instance::{Instance, NodeIdx},
    lower_bound::{self, PackingBound},
    reductions::{self, ReductionResult},
    report::{ReductionStats, Report, RootBounds, RuntimeStats, Settings, UpperBoundImprovement},
    small_indices::{IdxHashSet, SmallIdx},
};
use anyhow::{ensure, Result};
use log::{debug, info, trace, warn};
use std::time::Instant;

const ITERATION_LOG_INTERVAL_SECS: u64 = 60;

#[derive(Debug, Clone)]
pub struct State {
    pub partial_hs: Vec<NodeIdx>,
    pub minimum_hs: Vec<NodeIdx>,
    pub solve_start_time: Instant,
    pub last_log_time: Instant,
}

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
enum Status {
    /// Continue solving to search for smaller hitting sets
    Continue,

    /// A hitting set smaller or equal to the stopping size has been found
    Stop,
}

fn branch_on(
    node: NodeIdx,
    instance: &mut Instance,
    state: &mut State,
    report: &mut Report,
) -> Status {
    trace!("Branching on {}", node);
    report.branching_steps += 1;
    instance.delete_node(node);

    instance.delete_incident_edges(node);
    state.partial_hs.push(node);
    let status_without = solve_recursive(instance, state, report);
    debug_assert_eq!(state.partial_hs.last().copied(), Some(node));
    state.partial_hs.pop();
    instance.restore_incident_edges(node);

    if status_without == Status::Stop {
        instance.restore_node(node);
        return Status::Stop;
    }

    let status_with = solve_recursive(instance, state, report);
    instance.restore_node(node);
    status_with
}

fn solve_recursive(instance: &mut Instance, state: &mut State, report: &mut Report) -> Status {
    let now = Instant::now();
    if (now - state.last_log_time).as_secs() >= ITERATION_LOG_INTERVAL_SECS {
        info!(
            "Running on {} for {} branching steps",
            &report.file_name, report.branching_steps
        );
        state.last_log_time = now;
    }
    // info!("Time taken: {}", state.solve_start_time.elapsed().as_secs());
    // info!("{} {} {}",state.solve_start_time.elapsed().as_secs(),  report.settings.time_limit, state.solve_start_time.elapsed().as_secs() > report.settings.time_limit);
    if report.settings.time_limit != 0 && state.solve_start_time.elapsed().as_secs() > report.settings.time_limit {
        return Status::Stop;
    }

    let (reduction_result, reduction) = reductions::reduce(instance, state, report);
    let status = match reduction_result {
        ReductionResult::Solved => {
            if state.partial_hs.len() < state.minimum_hs.len() {
                info!("Found HS of size {} by branching", state.partial_hs.len());
                state.minimum_hs.clear();
                state.minimum_hs.extend(state.partial_hs.iter().copied());
                report.upper_bound_improvements.push(UpperBoundImprovement {
                    new_bound: state.minimum_hs.len(),
                    branching_steps: report.branching_steps,
                    runtime: state.solve_start_time.elapsed(),
                });
            } else {
                warn!(
                    "Found HS is not smaller than best known ({} vs. {}), should have been pruned",
                    state.partial_hs.len(),
                    state.minimum_hs.len(),
                );
            }

            if state.minimum_hs.len() <= report.settings.stop_at {
                Status::Stop
            } else {
                Status::Continue
            }
        }
        ReductionResult::Unsolvable => Status::Continue,
        ReductionResult::Stop => Status::Stop,
        ReductionResult::Finished => {
            let node = instance
                .nodes()
                .iter()
                .copied()
                .max_by_key(|&node| instance.node_degree(node))
                .expect("Branching on an empty instance");
            branch_on(node, instance, state, report)
        }
    };

    reduction.restore(instance, &mut state.partial_hs);
    status
}

fn is_hitting_set(hs: &[NodeIdx], instance: &Instance) -> bool {
    let hs_set: IdxHashSet<_> = hs.iter().copied().collect();
    instance
        .edges()
        .iter()
        .all(|&edge| instance.edge(edge).any(|node| hs_set.contains(&node)))
}

fn get_initial_hitting_set(instance: &Instance, settings: &Settings) -> Result<Vec<NodeIdx>> {
    if let Some(initial_hs) = &settings.initial_hitting_set {
        info!("Using initial hitting set from settings");
        debug!("Validating initial hitting set from settings");
        for &node in initial_hs {
            ensure!(
                node.idx() < instance.num_nodes_total(),
                "node index {} out of bounds in initial hitting set",
                node
            );
        }
        ensure!(
            is_hitting_set(initial_hs, instance),
            "initial hitting set is not valid"
        );

        Ok(initial_hs.clone())
    } else {
        Ok(instance.nodes().to_vec())
    }
}

fn calculate_root_bounds(instance: &Instance, settings: &Settings) -> RootBounds {
    let num_nodes = instance.num_nodes_total();
    let root_packing = PackingBound::new(instance, settings);
    RootBounds {
        max_degree: lower_bound::calc_max_degree_bound(instance).unwrap_or(num_nodes),
        sum_degree: lower_bound::calc_sum_degree_bound(instance),
        efficiency: lower_bound::calc_efficiency_bound(instance)
            .0
            .round()
            .unwrap_or(num_nodes),
        packing: root_packing.bound(),
        sum_over_packing: root_packing.calc_sum_over_packing_bound(instance),
        greedy_upper: reductions::calc_greedy_approximation(instance).len(),
    }
}

pub fn solve(
    mut instance: Instance,
    file_name: String,
    settings: Settings,
) -> Result<(Vec<NodeIdx>, Report)> {
    let initial_hs = get_initial_hitting_set(&instance, &settings)?;
    let root_bounds = calculate_root_bounds(&instance, &settings);
    let packing_from_scratch_limit = settings.packing_from_scratch_limit;
    let mut report = Report {
        file_name,
        opt: initial_hs.len(),
        branching_steps: 0,
        settings,
        root_bounds,
        runtimes: RuntimeStats::default(),
        reductions: ReductionStats::new(packing_from_scratch_limit),
        upper_bound_improvements: Vec::new(),
    };

    let mut state = State {
        partial_hs: Vec::new(),
        minimum_hs: initial_hs,
        last_log_time: Instant::now(),
        solve_start_time: Instant::now(),
    };
    let status = solve_recursive(&mut instance, &mut state, &mut report);
    report.runtimes.total = state.solve_start_time.elapsed();
    report.opt = state.minimum_hs.len();

    info!("Validating found hitting set");
    assert_eq!(instance.num_nodes_total(), instance.nodes().len());
    assert_eq!(instance.num_edges_total(), instance.edges().len());
    assert!(is_hitting_set(&state.minimum_hs, &instance));

    if status == Status::Continue {
        info!(
            "Found minimum hitting set in {:.2?} and {} branching steps",
            report.runtimes.total, report.branching_steps
        );
    } else {
        info!(
            "Found hitting set <= {} in {:.2?} and {} branching steps",
            report.settings.stop_at, report.runtimes.total, report.branching_steps
        );
    }
    debug!("Final HS (size {}): {:?}", report.opt, &state.minimum_hs);

    Ok((state.minimum_hs, report))
}
