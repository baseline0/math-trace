"""
Scenario: Cora Citation Network, Semi-Supervised Node Classification (Intermediate)

A two-layer graph convolutional network (Kipf & Welling 2017) on the Cora citation graph: 2708 papers, 1433 word
features, 7 topics. Only 140 papers are labelled for training, and the model predicts the topic of 1000 held-out
papers. Written in numpy with hand-derived gradients and Adam, so it needs no deep-learning framework.

Model (Â = D^{-1/2}(A + I)D^{-1/2}, X row-normalised):
    H = ReLU(Â X W₁)
    Z = Â H W₂
    loss = cross-entropy of softmax(Z) on the training nodes, plus L2 on W₁ and W₂

Run `python -m src.cora_data` first to create the converted dataset.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.sparse as sp

from ..cora_data import load_converted

DATA_DIR = Path(__file__).resolve().parents[2] / "generated" / "cora"


def row_normalise(features: sp.csr_matrix) -> sp.csr_matrix:
    """Divide each node's feature vector by its sum, so every row sums to one (rows of zeros stay zero)."""
    row_sums = np.asarray(features.sum(axis=1)).ravel()
    scale = np.zeros_like(row_sums, dtype=float)
    nonzero = row_sums > 0
    scale[nonzero] = 1.0 / row_sums[nonzero]
    return sp.diags(scale) @ features


def normalised_adjacency(A: sp.csr_matrix) -> sp.csr_matrix:
    """Â = D^{-1/2}(A + I)D^{-1/2}, the symmetric normalisation with self-loops."""
    A_hat = A + sp.identity(A.shape[0], format="csr")
    degree = np.asarray(A_hat.sum(axis=1)).ravel()
    inv_sqrt = 1.0 / np.sqrt(degree)
    D = sp.diags(inv_sqrt)
    return (D @ A_hat @ D).tocsr()


def init_params(n_in: int, n_hidden: int, n_out: int, seed: int = 0) -> dict[str, np.ndarray]:
    """Glorot-uniform initialisation of W₁ and W₂. The model has no biases, as in Kipf & Welling."""
    rng = np.random.default_rng(seed)
    limit1 = np.sqrt(6.0 / (n_in + n_hidden))
    limit2 = np.sqrt(6.0 / (n_hidden + n_out))
    return {
        "W1": rng.uniform(-limit1, limit1, size=(n_in, n_hidden)),
        "W2": rng.uniform(-limit2, limit2, size=(n_hidden, n_out)),
    }


def softmax(logits: np.ndarray) -> np.ndarray:
    """Row-wise softmax, shifted by the row maximum for stability."""
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)


def forward(params: dict[str, np.ndarray], AX: np.ndarray, A_hat: sp.csr_matrix) -> dict[str, np.ndarray]:
    """Forward pass, keeping the intermediate arrays the backward pass needs."""
    pre1 = AX @ params["W1"]
    H1 = np.maximum(pre1, 0.0)
    AH1 = A_hat @ H1
    logits = AH1 @ params["W2"]
    return {"pre1": pre1, "H1": H1, "AH1": AH1, "logits": logits}


def loss_and_gradients(
    params: dict[str, np.ndarray],
    AX: np.ndarray,
    A_hat: sp.csr_matrix,
    labels: np.ndarray,
    train_index: np.ndarray,
    weight_decay: float = 5e-4,
) -> tuple[float, dict[str, np.ndarray]]:
    """
    Cross-entropy on the training nodes, with L2 weight decay, and its gradients with respect to W₁ and W₂.

    dZ is nonzero only on training rows, and Â is symmetric, so dH = Â·dAH and dW₁ = (ÂX)ᵀ·(dH ⊙ ReLU'(pre1)).
    """
    cache = forward(params, AX, A_hat)
    probs = softmax(cache["logits"])
    n_train = len(train_index)

    picked = probs[train_index, labels[train_index]]
    data_loss = -np.log(np.maximum(picked, 1e-12)).mean()
    l2 = sum(float(np.sum(params[k] ** 2)) for k in ("W1", "W2"))
    loss = float(data_loss + 0.5 * weight_decay * l2)

    dZ = np.zeros_like(probs)
    dZ[train_index] = probs[train_index]
    dZ[train_index, labels[train_index]] -= 1.0
    dZ /= n_train

    dW2 = cache["AH1"].T @ dZ + weight_decay * params["W2"]
    dAH1 = dZ @ params["W2"].T
    dH1 = A_hat @ dAH1
    dpre1 = dH1 * (cache["pre1"] > 0)
    dW1 = AX.T @ dpre1 + weight_decay * params["W1"]

    return loss, {"W1": dW1, "W2": dW2}


def train(
    params: dict[str, np.ndarray],
    AX: np.ndarray,
    A_hat: sp.csr_matrix,
    labels: np.ndarray,
    train_index: np.ndarray,
    epochs: int = 200,
    lr: float = 0.01,
    weight_decay: float = 5e-4,
) -> tuple[dict[str, np.ndarray], list[float]]:
    """Full-batch Adam on the training loss. Returns the trained parameters and the loss per epoch."""
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    m = {k: np.zeros_like(v) for k, v in params.items()}
    v = {k: np.zeros_like(p) for k, p in params.items()}
    history = []
    params = {k: p.copy() for k, p in params.items()}

    for step in range(1, epochs + 1):
        loss, grads = loss_and_gradients(params, AX, A_hat, labels, train_index, weight_decay)
        history.append(loss)
        for k in params:
            m[k] = beta1 * m[k] + (1 - beta1) * grads[k]
            v[k] = beta2 * v[k] + (1 - beta2) * grads[k] ** 2
            m_hat = m[k] / (1 - beta1**step)
            v_hat = v[k] / (1 - beta2**step)
            params[k] = params[k] - lr * m_hat / (np.sqrt(v_hat) + eps)

    return params, history


def accuracy(logits: np.ndarray, labels: np.ndarray, index: np.ndarray) -> float:
    """Fraction of the given nodes whose highest-scoring class is correct."""
    return float(np.mean(np.argmax(logits[index], axis=1) == labels[index]))


def run_experiment(data_dir: Path = DATA_DIR, epochs: int = 200, seed: int = 0) -> dict:
    """Train the GCN on the converted Cora data and report training, validation, and test accuracy."""
    data = load_converted(data_dir)
    X = row_normalise(data["features"])
    A_hat = normalised_adjacency(data["adjacency"])
    AX = (A_hat @ X).toarray()

    params = init_params(X.shape[1], 16, 7, seed=seed)
    params, history = train(params, AX, A_hat, data["labels"], data["train_index"], epochs=epochs)
    logits = forward(params, AX, A_hat)["logits"]

    return {
        "params": params,
        "loss_history": history,
        "train_accuracy": accuracy(logits, data["labels"], data["train_index"]),
        "val_accuracy": accuracy(logits, data["labels"], data["val_index"]),
        "test_accuracy": accuracy(logits, data["labels"], data["test_index"]),
        "epochs": epochs,
    }


if __name__ == "__main__":
    result = run_experiment()

    print("=" * 70)
    print("Cora: two-layer GCN, 140 labelled training papers")
    print("=" * 70)
    print(
        f"\n  Loss: {result['loss_history'][0]:.3f} -> {result['loss_history'][-1]:.3f} over {result['epochs']} epochs"
    )
    print(f"  Train accuracy: {result['train_accuracy']:.3f}")
    print(f"  Validation accuracy: {result['val_accuracy']:.3f}")
    print(f"  Test accuracy: {result['test_accuracy']:.3f}")

    print("\n✅ Cora classification scenario complete")
