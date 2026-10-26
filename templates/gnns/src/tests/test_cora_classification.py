"""
Cora GCN contract tests.

Checks the hand-derived gradients against finite differences on a small graph, the normalisation properties,
and, when the converted dataset exists, that training reduces the loss and reaches the published accuracy range.
"""

import numpy as np
import pytest
import scipy.sparse as sp

from ..scenarios.cora_classification import (
    DATA_DIR,
    init_params,
    loss_and_gradients,
    normalised_adjacency,
    row_normalise,
    run_experiment,
)


def _small_graph():
    A = sp.csr_matrix(
        np.array(
            [
                [0, 1, 0, 0, 1, 0],
                [1, 0, 1, 0, 0, 0],
                [0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1],
                [1, 0, 0, 1, 0, 0],
                [0, 0, 0, 1, 0, 0],
            ],
            dtype=float,
        )
    )
    return A


class TestNormalisation:
    """Â is symmetric and row-normalised features sum to one."""

    def test_normalised_adjacency_is_symmetric(self):
        A_hat = normalised_adjacency(_small_graph())

        assert (A_hat != A_hat.T).nnz == 0

    def test_row_normalised_features_sum_to_one(self):
        features = sp.csr_matrix(np.array([[1.0, 3.0, 0.0], [0.0, 0.0, 0.0], [2.0, 2.0, 0.0]]))
        sums = np.asarray(row_normalise(features).sum(axis=1)).ravel()

        assert sums.tolist() == pytest.approx([1.0, 0.0, 1.0])


class TestGradients:
    """The analytic gradient of the training loss matches central finite differences."""

    @pytest.mark.parametrize("name", ["W1", "W2"])
    def test_gradient_matches_finite_differences(self, name):
        rng = np.random.default_rng(1)
        A_hat = normalised_adjacency(_small_graph())
        X = rng.normal(size=(6, 4))
        AX = A_hat @ X
        params = init_params(4, 3, 2, seed=3)
        labels = np.array([0, 1, 0, 1, 0, 1])
        train_index = np.array([0, 2, 3, 5])

        _loss, grads = loss_and_gradients(params, AX, A_hat, labels, train_index)
        numeric = np.zeros_like(params[name])
        eps = 1e-6
        for idx in np.ndindex(params[name].shape):
            plus = {k: v.copy() for k, v in params.items()}
            minus = {k: v.copy() for k, v in params.items()}
            plus[name][idx] += eps
            minus[name][idx] -= eps
            numeric[idx] = (
                loss_and_gradients(plus, AX, A_hat, labels, train_index)[0]
                - loss_and_gradients(minus, AX, A_hat, labels, train_index)[0]
            ) / (2 * eps)

        assert np.allclose(numeric, grads[name], atol=1e-7)


@pytest.fixture(scope="module")
def cora_result():
    return run_experiment(epochs=200)


@pytest.mark.skipif(not (DATA_DIR / "labels.npy").exists(), reason="run `python -m src.cora_data` first")
class TestCoraTraining:
    """Training on the converted Cora data reduces the loss and reaches the published accuracy range."""

    def test_loss_decreases(self, cora_result):
        assert cora_result["loss_history"][-1] < 0.5 * cora_result["loss_history"][0]

    def test_test_accuracy_in_published_range(self, cora_result):
        # Kipf & Welling (2017) report 81.5% on this split; allow a few points for the optimiser and seed.
        assert cora_result["test_accuracy"] >= 0.78

    def test_training_is_reproducible(self):
        first = run_experiment(epochs=20, seed=7)
        second = run_experiment(epochs=20, seed=7)

        assert first["loss_history"] == second["loss_history"]
