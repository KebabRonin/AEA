from typing import List, Set, Tuple
import time
import logging
import heapq

def read_hgr(file_path: str) -> Tuple[int, int, List[List[int]]]:
    num_nodes = 0
    num_edges = 0
    edges = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) != 4 or parts[1] != 'hs':
                    raise ValueError(f"Invalid problem line format: {line}")
                num_nodes = int(parts[2])
                num_edges = int(parts[3])
                continue
            vertices = [int(v) for v in line.split()]
            if not vertices:
                continue
            if any(v < 1 or v > num_nodes for v in vertices):
                raise ValueError(f"Vertex number out of range in line: {line}")
            edges.append(vertices)

    if not num_nodes or not num_edges:
        raise ValueError("Problem line not found or invalid")

    if len(edges) != num_edges:
        logging.warning(f"Expected {num_edges} edges but found {len(edges)}")

    return num_nodes, num_edges, edges

def is_hitting_set(hitting_set: Set[int], edges: List[Set[int]]) -> bool:
    return all(any(v in hitting_set for v in edge) for edge in edges)

def uncovered_edges(hitting_set: Set[int], edges: List[Set[int]]) -> List[Set[int]]:
    return [edge for edge in edges if not edge & hitting_set]

def solve_hitting_set(hyperedges: List[List[int]], time_limit: float = 10.0) -> List[int]:
    edges = [set(edge) for edge in hyperedges]
    universe = set(v for edge in edges for v in edge)
    best = [list(universe)]  # Initial worst-case solution

    start_time = time.time()
    heap = []  # Priority queue for best-first search
    initial_state = (0, set(), universe)  # (priority, current hitting set, available candidates)
    heapq.heappush(heap, initial_state)

    visited = 0

    while heap:
        if time.time() - start_time > time_limit:
            print(f"Terminated due to time limit after {time_limit:.2f} seconds.")
            break

        priority, current_set, candidates = heapq.heappop(heap)
        visited += 1

        if len(current_set) >= len(best[0]):
            continue

        remaining_edges = uncovered_edges(current_set, edges)
        if not remaining_edges:
            if len(current_set) < len(best[0]):
                best[0] = list(current_set)
                print(f"[{time.time() - start_time:.2f}s] Found new best: {best[0]}")
            continue

        vertex_score = {}
        for edge in remaining_edges:
            for v in edge:
                if v in candidates:
                    vertex_score[v] = vertex_score.get(v, 0) + 1

        if not vertex_score:
            continue

        sorted_vertices = sorted(vertex_score.items(), key=lambda x: -x[1])
        for v, _ in sorted_vertices:
            new_set = current_set | {v}
            new_candidates = candidates - {v}
            estimated_remaining = len(uncovered_edges(new_set, edges))
            estimated_cost = len(new_set) + estimated_remaining  # basic lower bound
            heapq.heappush(heap, (estimated_cost, new_set, new_candidates))

    print(f"Visited {visited} nodes in the search tree.")
    print(f"Completed in {time.time() - start_time:.2f} seconds.")
    return sorted(best[0])

# Example usage
if __name__ == "__main__":
    print(read_hgr("./hs_verifier/Hitting Set Verifier/src/test/resources/testset/bremen_subgraph_50.hgr"))
    hypergraph = [[13, 23, 28], [6, 15, 16, 31], [7, 8, 10, 17, 27], [12, 14, 18, 29], [11, 13, 23, 28],
                  [6, 15, 16, 20, 21], [15, 20, 21, 22], [14, 18, 19, 29], [4, 5, 8], [6, 16, 30, 31],
                  [7, 14, 18, 22, 26, 29, 32], [3, 11, 23, 24, 25], [2, 7, 17, 29, 32], [13, 23, 24, 28],
                  [12, 22, 26, 29], [8, 9, 10], [4, 5, 19], [1, 2, 27], [2, 30, 31, 32], [21, 22, 26, 29],
                  [9, 10, 17], [6, 15, 16, 31, 32], [1, 2, 7, 30], [1, 17, 27], [4, 8, 18, 19],
                  [7, 16, 29, 30, 32], [3, 24, 25], [15, 20, 21], [5, 8, 9, 17, 19], [11, 12, 13, 24],
                  [11, 12, 14, 26]]

    solution = solve_hitting_set(hypergraph, time_limit=260.0)
    print("Minimum Hitting Set:", solution)
    print("Size:", len(solution))
