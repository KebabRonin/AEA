
import docplex.cp.model as cplex


def get_queens_instance(n, blocked = []):
	mdl = cplex.CpoModel()
	lines = mdl.integer_var_list(n, 0, n - 1, "lines")
	mdl.add(mdl.all_diff(lines))
	mdl.add(mdl.all_diff(lines[i] + i for i in range(n)))
	mdl.add(mdl.all_diff(lines[i] - i for i in range(n)))

	return mdl

def print_sol(msol: cplex.CpoSolveResult):
	N = len(msol.get_all_var_solutions())
	for line in msol.get_all_var_solutions():
		line = line.get_value()
		print('_ '*line + '+ ' + '_ '*(N - line - 1))


N = 4
mdl = get_queens_instance(N)
msol = mdl.solve()
print(msol.get_solve_status())
print_sol(msol)