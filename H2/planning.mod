dvar float+ Gas;
dvar float+ Chloride;

maximize
	40 * Gas + 50 * Chloride;

subject to {
	ctMaxTotal:
		Gas + Chloride <= 50;
	ctMaxTotal2:
		3 * Gas + 4 * Chloride <= 180;
	ctMaxChloride:
		Chloride <= 40;
}

execute {
	writeln("Solution:")
	writeln("Gas Amount: ", Gas);
	writeln("Chloride Amount: ", Chloride);
	writeln("Profit: ", cplex.getObjValue())
}