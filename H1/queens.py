
import docplex.cp.model as cplex


def get_queens_instance(n, blocked = []):
	mdl = cplex.CpoModel()
	lines = mdl.integer_var_list(n, 0, n - 1, "lines")
	mdl.add(mdl.all_diff(lines))
	mdl.add(mdl.all_diff(lines[i] + i for i in range(n)))
	mdl.add(mdl.all_diff(lines[i] - i for i in range(n)))
	for b in blocked:
		mdl.add(lines[b[0]] != b[1])
	return mdl

def print_sol(msol: cplex.CpoSolveResult, blocked = []):
	N = len(msol.get_all_var_solutions())
	for line in range(N):
		line = msol.get_var_solution(f"lines_{line}").get_value()
		b = [b[1] for b in blocked if b[0] == line]
		for j in range(N):
			if j in b:
				print("X ", end = "")
			elif j == line:
				print("Q ", end = "")
			else:
				print("_ ", end = "")
		print("")

N = 4
# Blocked: list of (line, column)
blocked = [(0, 1), (0, 3)]
mdl = get_queens_instance(N, blocked)
msol = mdl.solve()
print(msol.get_solve_status())
if msol.get_solve_status() == "Feasible":
	print_sol(msol, blocked)