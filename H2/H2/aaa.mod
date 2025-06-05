// Parameters
int num_nodes;
int num_edges;

// Sets
{int} V = ...; // Vertex IDs
{int} E = ...; // Edge IDs

// Tuple for edge-vertex relation
tuple EdgeVertex {
  int e;
  int v;
}
{EdgeVertex} edge_vertices = ...;

// Decision variables
dvar boolean picked[V];

// Objective
minimize
  sum(v in V) picked[v];

// Constraints
subject to {
  forall(e in E)
    sum(ev in edge_vertices : ev.e == e) picked[ev.v] >= 1;
}
