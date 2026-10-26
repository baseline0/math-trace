"""
Cora conversion contract tests.

Offline tests check the loading safeguards: the unpickling allowlist, the pinned-digest check, and the shape checks.
The on-disk test runs only after `python -m src.cora_data` has written generated/cora/, and says so when skipped.
"""

import io
import os
import pickle
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from ..cora_data import (
    ALLOWED_GLOBALS,
    N_CLASSES,
    N_FEATURES,
    N_NODES,
    PINNED_SHA256,
    RestrictedUnpickler,
    check_dataset,
    fetch,
    load_converted,
)

GENERATED = Path(__file__).resolve().parents[2] / "generated" / "cora"


class TestUnpicklingAllowlist:
    """Loading a pickle that names a non-allowlisted global must fail before anything runs."""

    def test_rejects_os_global(self):
        payload = pickle.dumps(os.getcwd)  # references posix.getcwd; the restricted loader must refuse it

        with pytest.raises(pickle.UnpicklingError, match="allowlist"):
            RestrictedUnpickler(io.BytesIO(payload)).load()

    def test_allows_numpy_arrays(self):
        payload = pickle.dumps(np.arange(4))

        assert np.array_equal(RestrictedUnpickler(io.BytesIO(payload)).load(), np.arange(4))

    def test_allowlist_is_small(self):
        assert len(ALLOWED_GLOBALS) == 8


class TestPinnedDigests:
    """Every Planetoid file has a pinned digest, and a file that does not match it is refused."""

    def test_all_eight_files_pinned(self):
        assert set(PINNED_SHA256) == {"x", "y", "tx", "ty", "allx", "ally", "graph", "test.index"}

    def test_tampered_file_is_refused(self, tmp_path):
        for name in PINNED_SHA256:
            (tmp_path / f"ind.cora.{name}").write_bytes(b"not the published file")

        with pytest.raises(ValueError, match="does not match the pinned digest"):
            fetch(tmp_path)


class TestShapeChecks:
    """check_dataset refuses arrays that differ from the published Cora shapes."""

    @staticmethod
    def _valid():
        """A dataset with the published sizes: 5278 distinct undirected edges built from two ring offsets."""
        pairs = []
        seen = set()
        for k in (1, 2):
            for i in range(N_NODES):
                pair = frozenset((i, (i + k) % N_NODES))
                if pair not in seen:
                    seen.add(pair)
                    pairs.append(tuple(pair))
        pairs = pairs[:5278]
        rows = [a for a, _ in pairs] + [b for _, b in pairs]
        cols = [b for _, b in pairs] + [a for a, _ in pairs]
        adjacency = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N_NODES, N_NODES))
        return {
            "features": sp.random(N_NODES, N_FEATURES, density=0.01, format="csr", random_state=0),
            "labels": np.arange(N_NODES) % N_CLASSES,
            "adjacency": adjacency,
            "train_index": np.arange(140),
            "val_index": np.arange(140, 640),
            "test_index": np.arange(N_NODES - 1000, N_NODES),
        }

    def test_accepts_published_shapes(self):
        check_dataset(self._valid())

    def test_rejects_wrong_train_size(self):
        data = self._valid()
        data["train_index"] = np.arange(139)

        with pytest.raises(ValueError, match="train size"):
            check_dataset(data)


@pytest.fixture(scope="module")
def converted():
    return load_converted(GENERATED)


@pytest.mark.skipif(not (GENERATED / "labels.npy").exists(), reason="run `python -m src.cora_data` first")
class TestConvertedDataset:
    """The converted files have the published Cora sizes and class counts."""

    def test_passes_all_checks(self, converted):
        check_dataset(converted)

    def test_class_counts_match_published(self, converted):
        counts = np.bincount(converted["labels"], minlength=N_CLASSES)

        assert counts.tolist() == [351, 217, 418, 818, 426, 298, 180]

    def test_adjacency_has_no_self_loops(self, converted):
        assert converted["adjacency"].diagonal().sum() == 0
