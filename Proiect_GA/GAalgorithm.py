import numpy as np
import random
from collections import Counter
import time
import scipy.stats as stats
import matplotlib.pyplot as plt


# Load problem instance from file
def load_problem_instance(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    header = lines[0].strip().split()
    num_nodes = int(header[2])
    num_subsets = int(header[3])

    U = set(range(1, num_nodes + 1))
    S = [set(map(int, line.strip().split())) for line in lines[1:1 + num_subsets]]

    return U, S

# test_u, test_s = load_problem_instance('bremen_subgraph_300.txt')
# print(test_u)
# print(test_s)


# Problem-specific parameters
U = {1, 2, 3, 4, 5}  # Universal set
S = [{1, 2}, {2, 3, 4}, {1, 3, 4}, {4, 5}]  # Collection of subsets

U, S = load_problem_instance('bremen_subgraph_100.txt')

# Avem voie sa reparam indivizii care nu sunt corecti? sau doar  i verificam si le setam fitness la 0?
# sau nu i verificam deloc? asa doar o sa i facem pe toti 0? Sau poate modificam doar o valoare

POP_SIZE = 150
ITERATIONS = 5000
ELITE_COUNT = 100
MUTATION_RATE = 1/len(U)
LOCAL_SEARCH_RATE = 0.3  # on how many individuals we perform 2nd local search - x% of population
LS_INTERVAL = 100        # how often we perform 2nd local search (as iterations)

# we will precompute node frequencies in the subsets S, so that we can use it
# in a greedy way in a local search, in case a certain individual is not a hitting set
# GA is an optimization problem, but doesn't guarantee that an individual is certainly a solution
node_frequencies = Counter()
for subset in S:
    for elem in subset:
        node_frequencies[elem] += 1

bad_individuals = 0

print("We computed the node frequency in the set:")
print(node_frequencies)


# Initialize population (binary representation)
def initialize_population(individuals, nodes):
    return np.random.randint(2, size=(individuals, nodes))


# Initialize population - second method -> 3rd change
# here, for some individuals(sparse_fraction), we will tend to initialize them with fewer ones(only max_ones)
# hoping we can start with already better fitness that way
def initialize_population_some_sparse(individuals, nodes, sparse_fraction=0.3):
    max_ones = nodes // 3
    sparse_count = int(individuals * sparse_fraction)
    population = []

    # Sparse individuals
    for _ in range(sparse_count):
        individual = np.zeros(nodes, dtype=int)
        ones_count = random.randint(max_ones // 2, max_ones)
        ones_indices = random.sample(range(nodes), ones_count)
        for idx in ones_indices:
            individual[idx] = 1
        population.append(individual)

    # Random individuals
    for _ in range(individuals - sparse_count):
        population.append(np.random.randint(2, size=nodes))

    return np.array(population)

# Objective function: Number of selected nodes
def objective_function(individual):
    return np.sum(individual)  # Count of 1s


# check if an individual as a valid hitting set
def is_valid(individual):
    selected = {i+1 for i, val in enumerate(individual) if val == 1}
    return all(any(elem in selected for elem in subset) for subset in S)


# we perform a second local search in order to eliminate some 1 bits in certain individuals
# we do this only every LS_INTERVAL iterations, in order to keep time complexity down
# basically we just eliminate 1s and see if the individual is still valid, we do that
# in random selected individuals
def local_search(individual):
    for i in range(len(individual)):
        if individual[i] == 1:
            individual[i] = 0
            if not is_valid(individual):
                individual[i] = 1  # Revert if invalid
    return individual


# Ensure individual is a valid hitting set, if it's not a hitting set, we will make him a hitting set in a greedy way
# we will add nodes to him, in order of most frequent node that is not added, that's why we
# calculated the node_frequency variable
def repair_individual(individual):
    # Take the selected nodes for a certain individual by index, first index is 0 but the count of
    # nodes starts from one, that is why we add a + 1
    selected_nodes = {i + 1 for i, val in enumerate(individual) if val == 1}

    # Take all the subsets from S that have no node in the individual
    not_hitted_subsets = [subs for subs in S if not any(node in selected_nodes for node in subs)]

    if not not_hitted_subsets:
        return individual  # Already valid

    # we create a set with elements of the subsets that are not hitted
    missing_nodes = set()
    for subs in not_hitted_subsets:
        missing_nodes.update(subs)

    # Sort missing nodes by frequency (descending order)
    sorted_nodes = sorted(missing_nodes, key=lambda x: -node_frequencies[x])

    # Add nodes until all sets are hit
    for node in sorted_nodes:
        individual[node - 1] = 1
        selected_nodes.add(node)
        # check if adding the current node was enough, since
        if all(any(node in selected_nodes for node in subs) for subs in S):
            break

    return individual


# Fitness function: Normalize objective values and modify elite fitness
# we also perform a greedy local search here, in case a certain individual is not a hitting set, we will make him one
# this method is computational heavy, we will also try dropping them or randomly selecting another on in
# other fitness functions
def fitness_function_greedy_ls(population):
    # Repair individuals before fitness evaluation
    population = np.array([repair_individual(ind) for ind in population])

    obj_values = np.array([objective_function(ind) for ind in population])
    min_obj, max_obj = np.min(obj_values), np.max(obj_values)
    if min_obj == max_obj:
        fitness = np.ones(len(obj_values))  # Avoid division by zero
    else:
        fitness = 1 - (obj_values - min_obj) / (max_obj - min_obj)

    # print(f"Fitness before mean modification{fitness}")

    # Modify fitness to encourage diversity for the best ELITE_COUNT individuals
    sorted_indices = np.argsort(-fitness)  # Sort in descending order
    elite_indices = sorted_indices[:ELITE_COUNT]  # Get the top ELITE_COUNT individuals
    mean_fitness = np.mean(fitness)

    # here we apply the formula from the paper on the first ELITE COUNT(100-paper) individuals,
    # making their fitness 0 if they are less then the mean fitness
    for idx in elite_indices:
        if fitness[idx] > mean_fitness:
            fitness[idx] -= mean_fitness
        else:
            fitness[idx] = 0

    return fitness, population

# pop = initialize_population(7, len(U))
# print(pop)
# fitness = fitness_function(pop)
# print(f"Fitness after mean modification{fitness}")


# Rank-Based Selection
# this just orders the population by their fitness, and assigns probability to the selection process
# the best fitness gets the highest probability (the selection probability depends only on the rank!!!!)
# we try to keep diversity and not always only keep the best by this selection method
def rank_based_selection(population, fitness):
    size = len(population)
    # Get sorted indices of individuals (descending fitness)
    sorted_indices = np.argsort(-fitness)
    # Assign ranks (best = 0, worst = size-1)
    ranks = np.empty(size, dtype=int)
    for rank, idx in enumerate(sorted_indices):
        ranks[idx] = rank
    # Linear rank-based probabilities (you can use exponential if needed)
    rank_probs = np.array([size - r for r in ranks], dtype=float)
    rank_probs /= rank_probs.sum()  # Normalize to sum to 1
    # Select individuals using rank-based roulette wheel
    selected_indices = np.random.choice(size, size, p=rank_probs)
    return population[selected_indices]


# we apply tournament selection over all the individuals!
def tournament_selection(population, fitness, k=3):
    selected = []
    for _ in range(len(population)):
        # get k random indices, then add the index/individual which index returns the best fitness function
        contenders = random.sample(range(len(population)), k)
        best = max(contenders, key=lambda idx: fitness[idx])
        selected.append(population[best])
    return np.array(selected)


# we apply single-point cross-over at a random index and form 2 children
def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = np.concatenate((parent1[:point], parent2[point:]))
    child2 = np.concatenate((parent2[:point], parent1[point:]))
    return child1, child2


# mutation - flip a random bit
def mutate(individual):
    for i in range(len(individual)):
        if random.random() < MUTATION_RATE:
            individual[i] = 1 - individual[i]
    return individual


# Genetic Algorithm main loop
def genetic_algorithm():
    # init population and best global individual
    best_global_individual = np.random.randint(2, size=len(U))
    best_global_objective = 500
    # population = initialize_population(POP_SIZE, len(U))
    population = initialize_population_some_sparse(POP_SIZE, len(U))  # change 3
    best_obj_evolution = {}

    for iteration in range(ITERATIONS):
        # in this case we also return the population, because in the fitness function we modify it by local search
        # for first iteration we calculate fitness here
        if iteration == 0:
            fitness, population = fitness_function_greedy_ls(population)

        # Elitism: Keep the top individuals
        elite_indices = np.argsort(-fitness)[:ELITE_COUNT]
        new_population = population[elite_indices].tolist()

        # Selection and reproduction
        # selected = tournament_selection(population, fitness)
        selected = rank_based_selection(population, fitness)  # -> change 1

        while len(new_population) < POP_SIZE:
            p1, p2 = random.choices(selected, k=2)
            c1, c2 = crossover(p1, p2)
            c1, c2 = mutate(c1), mutate(c2)
            new_population.extend([c1, c2])

        population = np.array(new_population[:POP_SIZE])

        # Apply local search to a subset of population every LS_INTERVAL iterations -> change 2
        if iteration % LS_INTERVAL == 0:
            num_to_refine = int(LOCAL_SEARCH_RATE * POP_SIZE)
            indices = random.sample(range(len(population)), num_to_refine)
            for idx in indices:
                population[idx] = local_search(population[idx])

        # after applying genetic operators, we should check the fitness again
        fitness, population = fitness_function_greedy_ls(population)

        # check if best local solution is the best global solution
        best_idx = np.argmax(fitness)
        best_individual = population[best_idx]

        # check to make sure best individual is truly a hitting set
        # this will be useful later if we modify the local search, is just optional now
        nodes_in_best_individual = {i + 1 for i, val in enumerate(best_individual) if val == 1}
        not_hitted_subsets = [subs for subs in S if not any(node in nodes_in_best_individual for node in subs)]

        # change the best global individual only if valid!
        if not not_hitted_subsets:
            best_objective = objective_function(best_individual)
            if best_objective < best_global_objective:
                best_global_individual = best_individual
                best_global_objective = best_objective
                best_obj_evolution[iteration] = best_objective

        if iteration % 500 == 0:
            print(f"Iteration {iteration}: Best Obj = {best_global_objective}")

    best_obj_evolution[ITERATIONS] = best_global_objective
    # Return best solution
    return best_global_individual, best_global_objective, best_obj_evolution


# multiple runs for our alg
def run_multiple_experiments(n):
    objective_values = []
    times = []
    best_obj_evl_allr = {}

    for i in range(n):
        print(f"At run: {i+1}")
        start_time = time.time()
        best_solution, best_obj, best_obj_evl = genetic_algorithm()

        if len(objective_values) == 0:
            best_obj_evl_allr = dict(best_obj_evl)
        elif best_obj < min(objective_values):
            best_obj_evl_allr = dict(best_obj_evl)

        end_time = time.time()

        times.append(end_time - start_time)
        objective_values.append(best_obj)

    # Convert to numpy arrays
    obj_values = np.array(objective_values)
    times = np.array(times)

    # Compute statistics
    mean_obj = np.mean(obj_values)
    min_obj = np.min(obj_values)
    std_obj = np.std(obj_values, ddof=1)
    mean_time = np.mean(times)

    # 95% confidence interval for the median using t*
    confidence = 0.95
    alpha = 1 - confidence
    df = n - 1

    t_crit = stats.t.ppf(1 - alpha / 2, df)
    margin_error = t_crit * (std_obj / np.sqrt(n))

    # Step 6: Confidence interval
    ci_lower = mean_obj - margin_error
    ci_upper = mean_obj + margin_error

    plt.figure(figsize=(10, 6))
    iterations = list(best_obj_evl_allr.keys())
    objectives = list(best_obj_evl_allr.values())
    plt.plot(iterations, objectives, marker='o', linestyle='-')
    plt.title("Evolution Of Objective Value Over Iterations")
    plt.xlabel("Iteration")
    plt.ylabel("Objective Value")
    plt.grid(True)
    plt.tight_layout()
    # Save the plot to file
    plt.savefig("Grafice//IGA//brm100.png")
    plt.show()

    return {
        'mean_objective': mean_obj,
        'min_objective': min_obj,
        'std_objective': std_obj,
        'mean_time': mean_time,
        '95%_CI_median_objective': (ci_lower, ci_upper)
    }


# Run the algorithm
# start = time.time()
# best_solution, best_obj = genetic_algorithm()
# end = time.time()
# total_time = end-start
# print("Best solution:", best_solution)
# print("Objective function value:", best_obj)
# print(f"Function took {total_time:.4f} seconds to run.")

rs = run_multiple_experiments(30)
print(rs)


