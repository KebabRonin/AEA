import copy


class Instance:
    def __init__(self, edges, n_nodes, hit_nodes):
        self.edges = edges
        self.n_nodes = n_nodes
        self.hit_nodes = hit_nodes
    def parse(file_name):
        edges = []
        n_nodes = 0
        with open(file_name, 'rt') as f:
            for line in f.read_lines():
                pass
        return Instance(edges, n_nodes)
    def get_degree(self, idx):
        pass

class PartialSol:
    def __init__(self, instance):
        if instance is Instance:
            self.instance = Instance(instance)
            self.chosen = [None for _ in range(len(instance.edges))]
        elif instance is PartialSol:
            self.instance = Instance(instance.instance)
            self.chosen = copy.copy(instance.chosen)
    def choose(self, idx):
        new_sol = PartialSol(self)
        new_sol.chosen[idx] = True
        return new_sol
    def discard(self, idx):
        new_sol = PartialSol(self)
        new_sol.chosen[idx] = False
        return new_sol
    def score(self):
        return sum(self.chosen)
    def is_complete(self):
        pass
    def is_covered(self, ):
        pass


BEST_FOUND = PartialSol()
def bb_solve(instance: Instance, partial_sol=None):
    instance = copy.copy(instance)
    if BEST_FOUND.score():

    upper = greedy(instance)
    while instance.can_reduce():
        lower = get_lower(instance)
        if lower >= upper:
            return
        instance = reduce(instance)
    ## Select v
    v = 1
    bb_solve(instance, partial_sol.choose(v))
    bb_solve(instance, partial_sol.discard(v))