"""Unit tests: Graph Neural Network model validation.

Happy path tests for message passing, node updates, and graph operations.
"""

import importlib.util

import numpy as np

from math_trace.constants import REPO_ROOT

# Load gnns model module
gnns_model_path = REPO_ROOT / "templates" / "gnns" / "src" / "model.py"
spec = importlib.util.spec_from_file_location("gnns_model", gnns_model_path)
gnns_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gnns_model)

attention_weights = gnns_model.attention_weights
graph_attention_layer = gnns_model.graph_attention_layer
message_aggregate = gnns_model.message_aggregate
node_update = gnns_model.node_update


class TestMessageAggregation:
    """Validate message aggregation from neighbors."""

    def test_message_aggregate_sum(self):
        """Sum aggregation: m_i = ∑_j A_ij·h_j"""
        node_features = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        adjacency = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]])

        result = message_aggregate(node_features, adjacency, aggregation="sum")

        expected_0 = np.array([1.0, 2.0])
        assert np.allclose(result[0], expected_0)

    def test_message_aggregate_mean(self):
        """Mean aggregation: m_i = (1/degree) * ∑_j A_ij·h_j"""
        node_features = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        adjacency = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]])

        result = message_aggregate(node_features, adjacency, aggregation="mean")

        expected_0 = np.array([0.5, 1.0])
        assert np.allclose(result[0], expected_0, atol=1e-5)

    def test_message_aggregate_isolated_node(self):
        """Isolated node (no neighbors) should have zero aggregated message."""
        node_features = np.array([[1.0, 1.0], [0.0, 0.0], [1.0, 0.0]])
        adjacency = np.array([[1.0, 0.0, 1.0], [0.0, 0.0, 0.0], [1.0, 0.0, 1.0]])

        result = message_aggregate(node_features, adjacency, aggregation="sum")

        assert np.allclose(result[1], np.zeros(2))


class TestNodeUpdate:
    """Validate node feature updates."""

    def test_node_update_identity_weights(self):
        """With identity weights and bias=0, h'=σ(h+m)"""
        h = np.array([[1.0, 0.0], [0.0, 1.0]])
        m = np.array([[0.5, 0.5], [0.5, 0.5]])
        W_self = np.eye(2)
        W_neigh = np.eye(2)
        bias = np.zeros(2)

        result = node_update(h, m, W_self, W_neigh, bias, activation="relu")

        expected = np.array([[1.5, 0.5], [0.5, 1.5]])
        assert np.allclose(result, expected)

    def test_node_update_with_bias(self):
        """Bias should shift activations."""
        h = np.array([[1.0, 1.0]])
        m = np.array([[1.0, 1.0]])
        W_self = np.eye(2)
        W_neigh = np.eye(2)
        bias = np.array([0.5, 0.5])

        result = node_update(h, m, W_self, W_neigh, bias, activation="relu")

        expected = np.array([[2.5, 2.5]])
        assert np.allclose(result, expected)


class TestAttentionWeights:
    """Validate attention mechanism."""

    def test_attention_weights_softmax(self):
        """Attention weights sum to 1 (softmax property)."""
        scores = np.array([[1.0, 2.0, 3.0], [0.5, 0.5, 0.5]])
        weights = attention_weights(scores)

        row_sums = weights.sum(axis=1)
        assert np.allclose(row_sums, np.ones(2))

    def test_attention_weights_all_equal_scores(self):
        """Equal scores → uniform attention (1/n per neighbor)."""
        scores = np.array([[1.0, 1.0, 1.0]])
        weights = attention_weights(scores)

        expected = np.array([[1 / 3, 1 / 3, 1 / 3]])
        assert np.allclose(weights, expected, atol=1e-5)

    def test_attention_weights_monotonic(self):
        """Higher scores should get higher weights."""
        scores = np.array([[1.0, 5.0, 3.0]])
        weights = attention_weights(scores)

        assert weights[0, 1] > weights[0, 0]
        assert weights[0, 1] > weights[0, 2]


class TestGraphAttentionLayer:
    """Validate full graph attention layer."""

    def test_attention_layer_output_shape(self):
        """Output shape should match node count."""
        d_in = 3
        d_out = 2
        num_nodes = 4

        node_features = np.random.randn(num_nodes, d_in)
        adjacency = np.ones((num_nodes, num_nodes)) - np.eye(num_nodes)
        W = np.random.randn(d_in, d_out)
        a = np.random.randn(2 * d_out)

        result = graph_attention_layer(node_features, adjacency, W, a)

        assert result.shape[0] == num_nodes
