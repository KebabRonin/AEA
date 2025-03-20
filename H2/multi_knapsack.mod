int n = 4;
int c = 10;
range Items = 1..n;

int w[Items] = [2, 3, 4, 5];
int v[Items] = [3, 4, 5, 6];

dvar int+ x[Items];  

dexpr int tot_val = sum(i in Items) v[i] * x[i];  
dexpr int tot_weight = sum(i in Items) w[i] * x[i];

maximize tot_val;  

subject to {
  tot_weight <= c;
}

execute {
	writeln("Solution:");
    for (var i in Items) {
        writeln("Item ", i, ": ", x[i]);
    }

    writeln("Total Value: ", tot_val);
    writeln("Total Weight: ", tot_weight);
}
