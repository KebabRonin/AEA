import docplex.mp.model as cplex

mdl = cplex.Model()

Gas = mdl.continuous_var(name="Gas", lb=0)
Chloride = mdl.continuous_var(name="Chloride", lb=0)

mdl.maximize(40 * Gas + 50 * Chloride)

mdl.add_constraint(Gas + Chloride <= 50, "Max_Total")
mdl.add_constraint(3 * Gas + 4 * Chloride <= 180, "Max_Total2")
mdl.add_constraint(Chloride <= 40, "Max_Chloride")

solution = mdl.solve()

print(f"Gas: {solution[Gas]}")
print(f"Chloride: {solution[Chloride]}")
print(f"Profit: {solution.objective_value}")
