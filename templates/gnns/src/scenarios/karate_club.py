"""
Scenario: Zachary's Karate Club (Beginner)

Graph: 34 nodes (club members), 78 edges (friendships).
Task: Predict which faction each member joins after split.
"""

import numpy as np
from typing import Dict, Tuple
from ..model import message_aggregate, node_update, graph_attention_layer, classification_loss, graph_accuracy


def load_karate_club() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load Zachary's karate club graph.

    Returns:
        A: Adjacency matrix (34 × 34)
        labels: Ground truth (34,) with 0 or 1 for faction
        node_features: Initial features (34 × 1, all ones)
    """
    # Simplified adjacency (dense representation for demo)
    A = np.zeros((34, 34))

    edges = [
        (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8),
        (1,2), (1,3), (1,7),
        (2,3), (2,7), (2,8), (2,13),
        (3,4), (3,6), (3,10),
        (4,5), (4,6), (4,16),
        (5,6), (5,16),
        (6,16),
        (8,30), (8,32), (8,33),
        (13,33),
        (14,32), (14,33),
        (15,32), (15,33),
        (18,32), (18,33),
        (19,33),
        (20,32), (20,33),
        (22,32), (22,33),
        (23,25), (23,27), (23,29),
        (23,32), (23,33),
        (24,25), (24,28), (24,31),
        (25,31),
        (26,29), (26,33),
        (27,33),
        (28,31), (28,33),
        (29,32), (29,33),
        (30,32), (30,33),
        (31,32), (31,33),
        (32,33),
    ]

    for i, j in edges:
        A[i, j] = 1
        A[j, i] = 1

    # Add self-loops
    np.fill_diagonal(A, 1)

    # Ground truth: 0 = Faction A, 1 = Faction B
    labels = np.array([
        0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
        0, 0, 0, 0, 1, 1, 0, 0, 1, 0,
        1, 0, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1
    ])

    node_features = np.ones((34, 1))

    return A, labels, node_features


def simulate_gnn_inference(num_layers: int = 2) -> Dict:
    """
    Run GNN on karate club graph.

    Args:
        num_layers: Number of message-passing layers

    Returns:
        Dictionary with predictions, accuracy, node embeddings
    """
    A, labels, h = load_karate_club()
    num_nodes = A.shape[0]

    # Simple 1-layer GNN: aggregate → update → predict
    # (Full version would have multiple layers and learning)

    # Initialize random weights
    np.random.seed(42)
    W_self = np.random.randn(1, 8) * 0.1
    W_neigh = np.random.randn(1, 8) * 0.1
    bias = np.zeros(8)

    # Forward pass
    for layer in range(num_layers):
        m = message_aggregate(h, A, aggregation="mean")
        h = node_update(h, m, W_self, W_neigh, bias, activation="relu")

    # Classification head
    W_out = np.random.randn(h.shape[1], 2) * 0.1
    logits = h @ W_out

    # Softmax
    exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    predictions = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

    # Convert labels to one-hot
    labels_onehot = np.eye(2)[labels]

    loss = classification_loss(predictions, labels_onehot)
    acc = graph_accuracy(predictions, labels)

    return {
        "predictions": predictions,
        "embeddings": h,
        "loss": loss,
        "accuracy": acc,
        "num_nodes": num_nodes,
        "num_edges": np.sum(A) // 2,  # Count unique edges
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Zachary's Karate Club: Graph Neural Network")
    print("=" * 70)

    result = simulate_gnn_inference(num_layers=2)

    print(f"\nGraph Statistics:")
    print(f"  Nodes: {result['num_nodes']}")
    print(f"  Edges: {result['num_edges']}")

    print(f"\nModel Performance:")
    print(f"  Loss: {result['loss']:.4f}")
    print(f"  Accuracy: {result['accuracy']:.1%}")

    print("\n✅ Karate club scenario complete")
