Echipa Brassat Alexandru (IAO1) & Drumia Petru-Sebastian (IAO1) & Teodorescu Calin (SD1)

Proiect: [Hitting Set](https://pacechallenge.org/2025/hs/)

[BB paper](https://arxiv.org/pdf/2110.11697)

Proiectul GA in Proiect_GA (main: GAalgorithm.py)
Proiectul cplex in Proj (main: ilp.ipynb)
Proiectul bnb in bnb_rust (main: run_experiment.py)


To run bnb_rust: ([install rust](https://doc.rust-lang.org/cargo/getting-started/installation.html))

```sh
cd bnb_rust
cargo build
cargo run solve ../Proj/testset/bremen_subgraph_100.hgr settings.json --hgr --solution ../sol.json --report ../report.json
```
