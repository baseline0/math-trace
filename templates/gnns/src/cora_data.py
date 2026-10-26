"""
Cora citation network: download, verify, and convert to plain arrays.

The Planetoid release of Cora (Yang et al. 2016) ships as eight files. Seven are pickles, and a pickle runs
whatever it names when loaded, so this module does three things before any data is used:

1. Downloads each file to a cache directory and checks its SHA-256 against a pinned digest. A mismatch is an error.
2. Unpickles through an allowlist: only the globals the Planetoid files reference (numpy arrays, scipy CSR
   matrices, list, defaultdict) can be resolved. Any other global raises, so no code runs during loading.
3. Writes the dataset as plain arrays (npz without pickles), so the scenario never touches a pickle.

Usage (from templates/gnns):
    uv run python -m src.cora_data            # download, verify, convert into generated/cora/
"""

from __future__ import annotations

import hashlib
import pickle
import urllib.request
import warnings
from pathlib import Path

import numpy as np
import scipy.sparse as sp

PLANETOID_URL = "https://raw.githubusercontent.com/kimiyoung/planetoid/master/data/ind.cora.{name}"

# SHA-256 of each file as published at kimiyoung/planetoid, data/ (fetched 2026-10-26).
PINNED_SHA256 = {
    "x": "23cfa55d91c6f624233f5eb7b6e3f141f1bd2b2ae39608a63cf5d084bb27baab",
    "y": "94465c14eb53e04ca262198dcbb2521ee8af60fb3f3d546cd6ca24a511b0e7d1",
    "tx": "b9afbaa4a400df991f6f02ef677e1e44da55ffc04801fd02f9e673987829226a",
    "ty": "41f5ac76596a1699cc33f53084a2419e92961c42bb75f36fc38e616d348532ad",
    "allx": "9419ba2f26f5c35243db64aba110e0f35a04851609e0dc5433450676ca6b8543",
    "ally": "2b998f5cc7fedc86e7f97ca2498f47a1ffc1462c29e2d578b23bf3f62b6e7d71",
    "graph": "58f13302f39dde8852dad6fe6d15b89b077b6d7f837626bce671ef80344b383d",
    "test.index": "297ce89af2b51a6a194181c7dbe1796c6a1cf9cd9349a88383b1b1e227867875",
}

# The only globals the Planetoid pickles reference (checked with pickletools, not by loading).
ALLOWED_GLOBALS = {
    ("numpy", "dtype"),
    ("numpy", "ndarray"),
    ("numpy.core.multiarray", "_reconstruct"),  # older numpy path, as written in these pickles
    ("numpy._core.multiarray", "_reconstruct"),  # the same function under numpy 2.x
    ("scipy.sparse.csr", "csr_matrix"),
    ("builtins", "list"),
    ("__builtin__", "list"),  # Python 2 name for builtins.list, as written in these pickles
    ("collections", "defaultdict"),
}

N_FEATURES = 1433
N_CLASSES = 7
N_NODES = 2708
N_TRAIN = 140
N_VAL = 500
N_TEST = 1000
N_UNDIRECTED_EDGES = 5278  # standard count after removing duplicate and self-loop entries


class RestrictedUnpickler(pickle.Unpickler):
    """Unpickler that resolves only the allowlisted globals."""

    def find_class(self, module: str, name: str):
        if (module, name) not in ALLOWED_GLOBALS:
            raise pickle.UnpicklingError(f"global {module}.{name} is not on the Cora allowlist")
        return super().find_class(module, name)


def sha256_of(path: Path) -> str:
    """Hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(cache_dir: Path) -> dict[str, Path]:
    """Download any missing Planetoid files into cache_dir and verify every one against its pinned digest."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, expected in PINNED_SHA256.items():
        path = cache_dir / f"ind.cora.{name}"
        if not path.exists():
            urllib.request.urlretrieve(PLANETOID_URL.format(name=name), path)
        actual = sha256_of(path)
        if actual != expected:
            path.unlink()
            raise ValueError(f"{path.name}: SHA-256 {actual} does not match the pinned digest {expected}")
        paths[name] = path
    return paths


def _load_pickle(path: Path):
    with open(path, "rb") as f, warnings.catch_warnings():
        # The pickles name scipy.sparse.csr.csr_matrix; the warning is about that module path, not the data.
        warnings.filterwarnings("ignore", message="Please import `csr_matrix`", category=DeprecationWarning)
        return RestrictedUnpickler(f, encoding="latin1").load()


def _load_test_index(path: Path) -> np.ndarray:
    return np.array([int(line) for line in path.read_text().split()], dtype=np.int64)


def load_planetoid(paths: dict[str, Path]) -> dict[str, np.ndarray | sp.csr_matrix | dict]:
    """
    Assemble the standard Kipf-and-Welling split from the Planetoid files.

    Test nodes are stored out of order in the file, so the rows are reordered to match the node ids. Cora's test
    indices form one contiguous block, which this module checks; other Planetoid datasets have gaps and are out of scope.
    """
    tx = _load_pickle(paths["tx"])
    ty = _load_pickle(paths["ty"])
    allx = _load_pickle(paths["allx"])
    ally = _load_pickle(paths["ally"])
    graph = _load_pickle(paths["graph"])
    test_index = _load_test_index(paths["test.index"])

    test_sorted = np.sort(test_index)
    if not np.array_equal(test_sorted, np.arange(test_sorted[0], test_sorted[-1] + 1)):
        raise NotImplementedError("test indices are not one contiguous block; this loader handles Cora only")

    features = sp.vstack([allx, tx]).tolil()
    features[test_index, :] = features[test_sorted, :]
    labels_onehot = np.vstack([ally, ty])
    labels_onehot[test_index, :] = labels_onehot[test_sorted, :]

    adjacency = _adjacency_from_graph(graph, N_NODES)

    return {
        "features": features.tocsr(),
        "labels": np.argmax(labels_onehot, axis=1).astype(np.int64),
        "adjacency": adjacency,
        "train_index": np.arange(N_TRAIN, dtype=np.int64),
        "val_index": np.arange(N_TRAIN, N_TRAIN + N_VAL, dtype=np.int64),
        "test_index": test_index,
    }


def _adjacency_from_graph(graph: dict, n_nodes: int) -> sp.csr_matrix:
    """Symmetric binary adjacency without self-loops, from the Planetoid neighbour lists."""
    rows, cols = [], []
    for node, neighbours in graph.items():
        for other in neighbours:
            if other != node:
                rows.append(node)
                cols.append(other)
    adjacency = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n_nodes, n_nodes))
    adjacency = ((adjacency + adjacency.T) > 0).astype(np.float64)
    adjacency.setdiag(0)
    adjacency.eliminate_zeros()
    return adjacency.tocsr()


def check_dataset(data: dict) -> None:
    """Raise if the converted arrays do not have the published Cora shape and split sizes."""
    features = data["features"]
    checks = {
        "feature shape": features.shape == (N_NODES, N_FEATURES),
        "class count": int(data["labels"].max()) + 1 == N_CLASSES,
        "train size": len(data["train_index"]) == N_TRAIN,
        "val size": len(data["val_index"]) == N_VAL,
        "test size": len(data["test_index"]) == N_TEST,
        "undirected edges": int(data["adjacency"].nnz // 2) == N_UNDIRECTED_EDGES,
        "symmetric adjacency": (data["adjacency"] != data["adjacency"].T).nnz == 0,
        "splits disjoint": len(set(data["train_index"]) & set(data["val_index"]) & set(data["test_index"])) == 0,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise ValueError(f"Cora conversion failed checks: {', '.join(failed)}")


def convert(cache_dir: Path, out_dir: Path) -> dict:
    """Fetch, verify, load, check, and write the dataset as plain arrays. Returns the arrays written."""
    data = load_planetoid(fetch(cache_dir))
    check_dataset(data)

    out_dir.mkdir(parents=True, exist_ok=True)
    sp.save_npz(out_dir / "features.npz", data["features"])
    sp.save_npz(out_dir / "adjacency.npz", data["adjacency"])
    np.save(out_dir / "labels.npy", data["labels"], allow_pickle=False)
    np.savez(
        out_dir / "splits.npz",
        train=data["train_index"],
        val=data["val_index"],
        test=data["test_index"],
    )
    return data


def load_converted(out_dir: Path) -> dict:
    """Load the plain arrays written by convert(). Never unpickles anything."""
    return {
        "features": sp.load_npz(out_dir / "features.npz").tocsr(),
        "adjacency": sp.load_npz(out_dir / "adjacency.npz").tocsr(),
        "labels": np.load(out_dir / "labels.npy", allow_pickle=False),
        "train_index": np.load(out_dir / "splits.npz", allow_pickle=False)["train"],
        "val_index": np.load(out_dir / "splits.npz", allow_pickle=False)["val"],
        "test_index": np.load(out_dir / "splits.npz", allow_pickle=False)["test"],
    }


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    data = convert(
        cache_dir=Path.home() / ".cache" / "math-trace" / "cora-planetoid", out_dir=base / "generated" / "cora"
    )
    print(
        f"✅ Cora converted: {data['features'].shape[0]} nodes, {data['features'].shape[1]} features, "
        f"{int(data['adjacency'].nnz // 2)} undirected edges"
    )
    print(f"   train {len(data['train_index'])}, val {len(data['val_index'])}, test {len(data['test_index'])}")
