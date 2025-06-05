import time
from collections import defaultdict

def hitting_set_branch_and_bound(sets):
    # Convert sets to sets (not lists)
    sets = [set(s) for s in sets]
    universe = set().union(*sets)
    best_solution = [set(universe)]  # Initial best solution is the full universe

    # Precompute element -> sets mapping
    elem_to_sets = defaultdict(set)
    for i, s in enumerate(sets):
        for e in s:
            elem_to_sets[e].add(i)

    def branch(current_set, remaining_elements, uncovered_set_indices):
        if not uncovered_set_indices:
            if len(current_set) < len(best_solution[0]):
                best_solution[0] = current_set.copy()
            return

        if not remaining_elements:
            return

        if len(current_set) >= len(best_solution[0]):
            return

        # Heuristic: pick element covering most uncovered sets
        max_elem = None
        max_cover = -1
        for e in remaining_elements:
            cover = len(elem_to_sets[e] & uncovered_set_indices)
            if cover > max_cover:
                max_cover = cover
                max_elem = e

        if max_elem is None:
            return  # No element covers any remaining uncovered set

        # Exclude max_elem for next recursion
        new_remaining_elements = remaining_elements - {max_elem}

        # Sets hit by max_elem
        newly_covered_sets = elem_to_sets[max_elem] & uncovered_set_indices
        new_uncovered_set_indices = uncovered_set_indices - newly_covered_sets

        # Branch: include max_elem
        branch(current_set | {max_elem}, new_remaining_elements, new_uncovered_set_indices)
        # Branch: exclude max_elem
        branch(current_set, new_remaining_elements, uncovered_set_indices)

    # Initial call
    branch(set(), set(universe), set(range(len(sets))))
    return best_solution[0]

# Example usage
if __name__ == "__main__":
    sets = [
        [13, 23, 28], [6, 15, 16, 31], [7, 8, 10, 17, 27], [12, 14, 18, 29], [11, 13, 23, 28],
        [6, 15, 16, 20, 21], [15, 20, 21, 22], [14, 18, 19, 29], [4, 5, 8], [6, 16, 30, 31],
        [7, 14, 18, 22, 26, 29, 32], [3, 11, 23, 24, 25], [2, 7, 17, 29, 32], [13, 23, 24, 28],
        [12, 22, 26, 29], [8, 9, 10], [4, 5, 19], [1, 2, 27], [2, 30, 31, 32], [21, 22, 26, 29],
        [9, 10, 17], [6, 15, 16, 31, 32], [1, 2, 7, 30], [1, 17, 27], [4, 8, 18, 19],
        [7, 16, 29, 30, 32], [3, 24, 25], [15, 20, 21], [5, 8, 9, 17, 19], [11, 12, 13, 24],
        [11, 12, 14, 26]
    ]

    start_time = time.time()
    result = hitting_set_branch_and_bound(sets)
    end_time = time.time()

    print("Optimal hitting set:", result)
    print("Time taken:", end_time - start_time, "seconds")