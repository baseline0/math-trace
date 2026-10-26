# Graph Neural Networks

Message passing, graph attention, and node classification on graph-structured data.

## Scenarios

- **Scenario 1: Zachary's Karate Club** (34 nodes, friendship split prediction)
  ```bash
  uv run python -m src.scenarios.karate_club
  ```
- **Scenario 2: Cora Citation Network** (2708 papers, 7 topics, semi-supervised node classification with a
  two-layer GCN written in numpy; test accuracy about 81%)
  ```bash
  uv run python -m src.cora_data               # download, verify, and convert Cora (once)
  uv run python -m src.scenarios.cora_classification
  ```

## Cora data

The Planetoid release ships seven of its eight files as pickles, and loading a pickle runs code. The conversion
step therefore:

1. downloads each file from `kimiyoung/planetoid` and checks its SHA-256 against a pinned digest;
2. unpickles only the globals those files reference (numpy arrays, scipy CSR matrices, lists, defaultdict);
3. writes plain `.npz` and `.npy` arrays to `generated/cora/`, which the scenario reads without pickles.

## Tests

```bash
uv run pytest src/tests
```

The Cora training tests are skipped until `generated/cora/` exists.

## References

- Kipf & Welling (2017): Semi-Supervised Classification with Graph Convolutional Networks (ICLR)
- Veličković et al. (2017): Graph Attention Networks
- Gilmer et al. (2017): Neural Message Passing for Quantum Chemistry
- Yang, Cohen & Salakhutdinov (2016): Revisiting Semi-Supervised Learning with Graph Embeddings (Planetoid data)
