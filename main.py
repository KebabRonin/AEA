import time
from collections import Counter

def hitting_set_branch_and_bound(sets):
    # Remove redundant sets: if a set is a superset of another, drop the larger one
    def reduce_sets(sets):
        sets = [set(s) for s in sets]
        reduced = []
        for s1 in sets:
            if not any(s1 > s2 for s2 in sets if s1 != s2):
                reduced.append(s1)
        return reduced

    sets = reduce_sets(sets)
    universe = set().union(*sets)
    best_solution = [set(universe)]  # Initial best solution: full universe

    # Greedy initial solution
    uncovered = sets[:]
    greedy_solution = set()
    while uncovered:
        # Pick element that covers most uncovered sets
        e = max(universe, key=lambda e: sum(e in s for s in uncovered))
        greedy_solution.add(e)
        uncovered = [s for s in uncovered if e not in s]
    best_solution[0] = greedy_solution.copy()

    # Lower bound: at least as many elements as the number of uncovered sets
    def lower_bound(uncovered_sets):
        return max((1 for s in uncovered_sets), default=0)

    def branch(current_set, remaining_elements, uncovered_sets):
        if not uncovered_sets:
            if len(current_set) < len(best_solution[0]):
                best_solution[0] = current_set.copy()
            return

        if not remaining_elements:
            return

        # Prune: too many elements already
        if len(current_set) + lower_bound(uncovered_sets) >= len(best_solution[0]):
            return

        # Heuristic: pick element covering most uncovered sets
        freq = Counter()
        for s in uncovered_sets:
            for e in s:
                if e in remaining_elements:
                    freq[e] += 1
        if not freq:
            return
        e = max(freq, key=freq.get)

        new_remaining = remaining_elements - {e}
        new_uncovered_sets = [s for s in uncovered_sets if e not in s]

        # Branch: include e
        branch(current_set | {e}, new_remaining, new_uncovered_sets)
        # Branch: exclude e
        branch(current_set, new_remaining, uncovered_sets)

    branch(set(), set(universe), sets)
    return best_solution[0]


# Example usage
if __name__ == "__main__":
    # sets = [
    #     [8, 9, 12, 47, 55], [23, 24, 25, 61], [9, 14, 55, 56], [24, 49, 61], [27, 31, 32, 49], [17, 62, 63],
    #     [9, 13, 14, 48, 59], [12, 18, 20, 33, 60], [22, 23, 26, 28, 45], [30, 35, 39, 40], [8, 11, 12, 54, 60],
    #     [4, 27, 32, 37, 45], [4, 22, 32, 45, 46], [44, 52, 53], [34, 38, 39, 40], [32, 36, 37, 47],
    #     [26, 41, 42, 43], [9, 27, 31, 47, 48], [15, 44, 51, 55], [2, 3, 35], [10, 20, 21, 57, 60],
    #     [7, 16, 19], [11, 52, 53, 54], [50, 62, 63], [17, 49, 50, 62], [2, 3, 11, 35], [10, 20, 34, 57, 58],
    #     [21, 34, 38, 39, 57], [6, 28, 29], [13, 31, 48, 49, 50], [1, 6, 7, 19, 33], [44, 51, 52, 54],
    #     [17, 27, 48, 49, 61], [1, 7, 10, 58], [16, 19, 42], [22, 28, 29], [14, 15, 51], [2, 3, 35, 40],
    #     [6, 7, 29, 46], [12, 44, 53, 54, 55], [24, 25, 43], [22, 23, 24, 26], [4, 18, 36, 37],
    #     [8, 51, 54, 55, 56], [13, 14, 15, 56], [16, 41, 42], [11, 21, 30, 40], [5, 6, 45, 46], [20, 21, 30, 34],
    #     [4, 5, 18, 33, 46], [3, 11, 12, 30, 53], [25, 41, 43], [17, 48, 50, 59, 63], [34, 38, 39],
    #     [22, 23, 26, 41], [5, 7, 10, 33, 60], [1, 57, 58], [8, 9, 13, 31, 56], [5, 18, 36, 60],
    #     [1, 10, 20, 33, 57], [4, 5, 32, 36, 45], [13, 50, 59], [8, 31, 37, 47]
    # ]
    sets = [[13, 23, 28], [6, 15, 16, 31], [7, 8, 10, 17, 27], [12, 14, 18, 29], [11, 13, 23, 28],
                  [6, 15, 16, 20, 21], [15, 20, 21, 22], [14, 18, 19, 29], [4, 5, 8], [6, 16, 30, 31],
                  [7, 14, 18, 22, 26, 29, 32], [3, 11, 23, 24, 25], [2, 7, 17, 29, 32], [13, 23, 24, 28],
                  [12, 22, 26, 29], [8, 9, 10], [4, 5, 19], [1, 2, 27], [2, 30, 31, 32], [21, 22, 26, 29],
                  [9, 10, 17], [6, 15, 16, 31, 32], [1, 2, 7, 30], [1, 17, 27], [4, 8, 18, 19],
                  [7, 16, 29, 30, 32], [3, 24, 25], [15, 20, 21], [5, 8, 9, 17, 19], [11, 12, 13, 24],
                  [11, 12, 14, 26]]

    start_time = time.time()
    result = hitting_set_branch_and_bound(sets)
    end_time = time.time()

    print("Optimal hitting set:", result)
    print("Time taken:", end_time - start_time, "seconds")