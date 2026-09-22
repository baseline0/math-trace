"""
Graph Neural Networks: Message Passing & Attention

Graph convolutional layers, attention mechanisms, node classification.

References:
- Kipf & Welling (2016): Semi-Supervised Classification with GCNs
- Veličković et al. (2017): Graph Attention Networks
- Gilmer et al. (2017): Neural Message Passing for Quantum Chemistry
"""

import numpy as np
import json
from typing import Tuple, Dict, Any, List


# ============================================================================
# Equation 1: Message Aggregation (Graph Convolution)
# ============================================================================
# m_i = ∑_j ∈ N(i) h_j  (sum neighbors)
# or: m_i = ∑_j ∈ N(i) A_ij·h_j  (weighted by adjacency)
#
# Code Reference: message_aggregate()

def message_aggregate(
    node_features: np.ndarray,
    adjacency: np.ndarray,
    aggregation: str = "sum"
) -> np.ndarray:
    """
    Aggregate messages from neighbors.

    m_i = ∑_j ∈ N(i) w_ij·h_j

    Args:
        node_features: Node embeddings h (num_nodes × feature_dim)
        adjacency: Adjacency matrix A (num_nodes × num_nodes)
        aggregation: "sum", "mean", or "max"

    Returns:
        Aggregated messages (num_nodes × feature_dim)
    """
    # Adjacency @ features: matrix multiplication
    aggregated = adjacency @ node_features

    if aggregation == "mean":
        # Normalize by degree
        degree = np.sum(adjacency, axis=1, keepdims=True)
        degree[degree == 0] = 1  # Avoid division by zero
        aggregated = aggregated / degree
    elif aggregation == "max":
        # Max pooling (approximate with log-sum-exp)
        aggregated = np.log(np.exp(adjacency @ node_features).sum(axis=1, keepdims=True) + 1e-10)

    return aggregated


# ============================================================================
# Equation 2: Node Update (Feature Transformation)
# ============================================================================
# h'_i = σ(W_self·h_i + W_neigh·m_i + b)
#
# Code Reference: node_update()

def node_update(
    node_features: np.ndarray,
    messages: np.ndarray,
    W_self: np.ndarray,
    W_neigh: np.ndarray,
    bias: np.ndarray,
    activation: str = "relu"
) -> np.ndarray:
    """
    Update node embeddings using aggregated messages.

    h'_i = σ(W_self·h_i + W_neigh·m_i + b)

    Args:
        node_features: Current h (num_nodes × d_in)
        messages: Aggregated m (num_nodes × d_in)
        W_self: Self-connection weight (d_in × d_out)
        W_neigh: Neighbor weight (d_in × d_out)
        bias: Bias term (d_out,)
        activation: "relu", "tanh", or "sigmoid"

    Returns:
        Updated h' (num_nodes × d_out)
    """
    # Linear combination
    h_new = (node_features @ W_self) + (messages @ W_neigh) + bias

    # Activation
    if activation == "relu":
        h_new = np.maximum(0, h_new)
    elif activation == "tanh":
        h_new = np.tanh(h_new)
    elif activation == "sigmoid":
        h_new = 1 / (1 + np.exp(-h_new))

    return h_new


# ============================================================================
# Equation 3: Attention Weights (Softmax)
# ============================================================================
# α_ij = softmax_j(a_ij) = exp(a_ij) / ∑_k exp(a_ik)
#
# Code Reference: attention_weights()

def attention_weights(
    attention_logits: np.ndarray,
    mask: np.ndarray = None
) -> np.ndarray:
    """
    Compute attention weights via softmax.

    α_ij = exp(a_ij) / ∑_k exp(a_ik)

    Args:
        attention_logits: Raw attention scores (num_nodes × num_nodes)
        mask: Optional mask for valid edges

    Returns:
        Normalized attention weights (num_nodes × num_nodes)
    """
    if mask is not None:
        attention_logits = attention_logits * mask
        attention_logits = np.where(mask == 0, -1e9, attention_logits)

    # Softmax with numerical stability
    exp_logits = np.exp(attention_logits - np.max(attention_logits, axis=1, keepdims=True))

    # Sum along neighbors (axis 1)
    sum_exp = np.sum(exp_logits, axis=1, keepdims=True)
    sum_exp[sum_exp == 0] = 1  # Avoid division by zero

    return exp_logits / sum_exp


# ============================================================================
# Equation 4: Graph Attention Layer
# ============================================================================
# α_ij = softmax(a^T · [W·h_i || W·h_j])
# h'_i = σ(∑_j α_ij·W·h_j)
#
# Code Reference: graph_attention_layer()

def graph_attention_layer(
    node_features: np.ndarray,
    adjacency: np.ndarray,
    W: np.ndarray,
    a: np.ndarray,
    activation: str = "relu"
) -> np.ndarray:
    """
    Single graph attention layer.

    Args:
        node_features: h (num_nodes × d_in)
        adjacency: A (num_nodes × num_nodes)
        W: Linear transform (d_in × d_out)
        a: Attention vector (d_out,)
        activation: Activation function

    Returns:
        Updated h' (num_nodes × d_out)
    """
    # Transform features
    h_transformed = node_features @ W  # (num_nodes × d_out)

    # Compute attention logits
    num_nodes = node_features.shape[0]
    attention_logits = np.zeros((num_nodes, num_nodes))

    for i in range(num_nodes):
        for j in range(num_nodes):
            # a^T · [h_i || h_j] (concatenation attention)
            combined = np.concatenate([h_transformed[i], h_transformed[j]])
            attention_logits[i, j] = np.dot(a, combined)

    # Apply softmax
    alpha = attention_weights(attention_logits, mask=adjacency.astype(bool).astype(float))

    # Aggregate with attention
    h_new = alpha @ h_transformed

    # Apply activation
    if activation == "relu":
        h_new = np.maximum(0, h_new)

    return h_new


# ============================================================================
# Equation 5: Graph Classification Loss (Cross-Entropy)
# ============================================================================
# L = -∑_i y_i·log(ŷ_i)  (node classification)
#
# Code Reference: classification_loss()

def classification_loss(
    predictions: np.ndarray,
    labels: np.ndarray
) -> float:
    """
    Cross-entropy loss for node classification.

    L = -∑_i ∑_c y_ic·log(ŷ_ic)

    Args:
        predictions: Predicted probabilities (num_nodes × num_classes)
        labels: One-hot encoded labels (num_nodes × num_classes)

    Returns:
        Scalar loss value
    """
    # Clamp predictions to avoid log(0)
    predictions = np.clip(predictions, 1e-7, 1 - 1e-7)

    # Cross-entropy
    loss = -np.sum(labels * np.log(predictions)) / len(labels)

    return loss


def graph_accuracy(
    predictions: np.ndarray,
    labels: np.ndarray,
    mask: np.ndarray = None
) -> float:
    """
    Accuracy for node classification.

    Args:
        predictions: Predicted class indices or probabilities
        labels: True class indices or one-hot labels
        mask: Optional mask for which nodes to evaluate

    Returns:
        Accuracy (fraction correct)
    """
    if predictions.ndim == 2:
        pred_labels = np.argmax(predictions, axis=1)
    else:
        pred_labels = predictions

    if labels.ndim == 2:
        true_labels = np.argmax(labels, axis=1)
    else:
        true_labels = labels

    if mask is not None:
        pred_labels = pred_labels[mask]
        true_labels = true_labels[mask]

    return np.mean(pred_labels == true_labels)


def export_equation_metadata() -> Dict[str, Any]:
    """Auto-generate equations.json for paper.typ."""
    return {
        "message_aggregation": {
            "latex": r"m_i = \sum_{j \in N(i)} A_{ij} \mathbf{h}_j",
            "code_ref": "model.py:message_aggregate()",
            "line": 31,
            "description": "Neighbor aggregation via matrix multiplication",
        },
        "node_update": {
            "latex": r"\mathbf{h}'_i = \sigma(W_{\text{self}} \mathbf{h}_i + W_{\text{neigh}} \mathbf{m}_i + \mathbf{b})",
            "code_ref": "model.py:node_update()",
            "line": 77,
            "description": "Update node with self + aggregated neighbor info",
        },
        "attention_softmax": {
            "latex": r"\alpha_{ij} = \frac{\exp(a_{ij})}{\sum_k \exp(a_{ik})}",
            "code_ref": "model.py:attention_weights()",
            "line": 119,
            "description": "Softmax normalization for attention",
        },
        "graph_attention": {
            "latex": r"\mathbf{h}'_i = \sigma\left(\sum_j \alpha_{ij} W \mathbf{h}_j\right)",
            "code_ref": "model.py:graph_attention_layer()",
            "line": 158,
            "description": "Attention-weighted neighbor aggregation",
        },
        "cross_entropy_loss": {
            "latex": r"L = -\sum_i \sum_c y_{ic} \log(\hat{y}_{ic})",
            "code_ref": "model.py:classification_loss()",
            "line": 206,
            "description": "Node classification cross-entropy loss",
        },
    }


if __name__ == "__main__":
    metadata = export_equation_metadata()
    with open("equations.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Exported equations.json")
