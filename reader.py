
def read_hgr(file_path: str|int):
    if isinstance(file_path, int):
        file_path = f"./hs_verifier/Hitting Set Verifier/src/test/resources/testset/bremen_subgraph_{file_path}.hgr"
    num_nodes = 0
    num_edges = 0
    edges = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) != 4 or parts[1] != 'hs':
                    raise ValueError(f"Invalid problem line format: {line}")
                num_nodes = int(parts[2])
                num_edges = int(parts[3])
                continue
            vertices = [int(v) for v in line.split()]
            if not vertices:
                continue
            if any(v < 1 or v > num_nodes for v in vertices):
                raise ValueError(f"Vertex number out of range in line: {line}")
            edges.append(vertices)

    if not num_nodes or not num_edges:
        raise ValueError("Problem line not found or invalid")

    if len(edges) != num_edges:
        raise ValueError("Not enough edges")

    return num_nodes, num_edges, edges
