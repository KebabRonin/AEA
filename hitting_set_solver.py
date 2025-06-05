from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass
import time
from collections import defaultdict
import logging

@dataclass
class Settings:
    stop_at: int = float('inf')
    initial_hitting_set: Optional[List[int]] = None
    packing_from_scratch_limit: int = 1000

class HittingSetSolver:
    def __init__(self, edges: List[List[int]], settings: Settings = Settings()):
        self.edges = edges
        self.settings = settings
        self.vertex_to_edges: Dict[int, Set[int]] = defaultdict(set)
        self.edge_to_vertices: Dict[int, Set[int]] = defaultdict(set)

        for edge_idx, edge in enumerate(edges):
            for vertex in edge:
                self.vertex_to_edges[vertex].add(edge_idx)
                self.edge_to_vertices[edge_idx].add(vertex)

        self.num_vertices = max(max(edge) for edge in edges) + 1 if edges else 0
        self.num_edges = len(edges)

    def is_hitting_set(self, hitting_set: List[int]) -> bool:
        hitting_set_set = set(hitting_set)
        return all(any(vertex in hitting_set_set for vertex in self.edge_to_vertices[edge_idx])
                   for edge_idx in range(self.num_edges))

    def get_vertex_degree(self, vertex: int) -> int:
        return len(self.vertex_to_edges[vertex])

    def delete_vertex(self, vertex: int) -> Set[int]:
        affected_edges = self.vertex_to_edges[vertex].copy()
        for edge_idx in affected_edges:
            self.edge_to_vertices[edge_idx].remove(vertex)
        self.vertex_to_edges[vertex].clear()
        return affected_edges

    def restore_vertex(self, vertex: int, affected_edges: Set[int]):
        for edge_idx in affected_edges:
            self.edge_to_vertices[edge_idx].add(vertex)
            self.vertex_to_edges[vertex].add(edge_idx)

    def find_best_vertex(self) -> Tuple[int, int]:
        max_degree = -1
        best_vertex = -1
        for vertex in range(self.num_vertices):
            if vertex in self.excluded_vertices:
                continue
            degree = self.get_vertex_degree(vertex)
            if degree > max_degree:
                max_degree = degree
                best_vertex = vertex
        return best_vertex, max_degree

    def solve(self) -> List[int]:
        initial_solution = list(range(self.num_vertices))
        if self.settings.initial_hitting_set:
            if self.is_hitting_set(self.settings.initial_hitting_set):
                initial_solution = self.settings.initial_hitting_set
            else:
                raise ValueError("Provided initial hitting set is not valid")

        self.best_solution = initial_solution
        self.partial_solution = []
        self.excluded_vertices = set()
        self.start_time = time.time()

        # Stack holds (vertex, include_vertex, affected_edges or None)
        stack = [(None, True, set())]

        while stack:
            vertex, include_vertex, affected_edges = stack.pop()

            if vertex is not None:
                if include_vertex:
                    self.restore_vertex(vertex, affected_edges)
                    self.partial_solution.pop()
                else:
                    self.excluded_vertices.remove(vertex)
                    continue

            if len(self.partial_solution) >= len(self.best_solution):
                continue

            best_vertex, max_degree = self.find_best_vertex()

            if max_degree == 0:
                if len(self.partial_solution) < len(self.best_solution):
                    self.best_solution = self.partial_solution.copy()
                    if len(self.best_solution) <= self.settings.stop_at:
                        break
                continue

            vertex = best_vertex

            # Branch: exclude vertex
            self.excluded_vertices.add(vertex)
            stack.append((vertex, False, None))

            # Branch: include vertex
            self.partial_solution.append(vertex)
            affected_edges = self.delete_vertex(vertex)
            stack.append((vertex, True, affected_edges))

        return self.best_solution

def solve_hitting_set(edges: List[List[int]], settings: Settings = Settings()) -> List[int]:
    solver = HittingSetSolver(edges, settings)
    return solver.solve()

# Example usage
if __name__ == "__main__":
    edges = [
        [0, 1, 2],
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5]
    ]

    solution = solve_hitting_set(edges)
    print(f"Minimum hitting set: {solution}")
    print(f"Size: {len(solution)}")

    settings = Settings(
        stop_at=3,
        initial_hitting_set=[1, 3, 5]
    )
    solution = solve_hitting_set(edges, settings)
    print(f"\nMinimum hitting set with custom settings: {solution}")
    print(f"Size: {len(solution)}")
