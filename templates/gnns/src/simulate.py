"""GNN simulations: message passing and graph classification."""

import numpy as np

def graph_representation(num_nodes: int = 5) -> dict:
    """Create a simple graph representation."""
    # Random adjacency matrix (undirected)
    A = np.random.rand(num_nodes, num_nodes)
    A = (A + A.T) / 2  # Make symmetric
    A = (A > 0.5).astype(int)  # Threshold to 0/1
    np.fill_diagonal(A, 0)  # No self-loops
    
    return {"adjacency": A, "num_nodes": num_nodes, "num_edges": np.sum(A) // 2}

def message_passing_layer(features: np.ndarray, adjacency: np.ndarray, weight: float = 0.5):
    """Single GNN layer: aggregate neighbor features."""
    # Message from neighbors: A @ h
    messages = adjacency @ features
    # Update: h' = weight * h + (1 - weight) * messages
    updated = weight * features + (1 - weight) * messages
    return updated

def node_classification_demo(num_nodes: int = 5, num_layers: int = 3):
    """Simulate GNN node classification."""
    # Random initial features
    h = np.random.randn(num_nodes, 2)
    A = np.random.rand(num_nodes, num_nodes) > 0.6
    A = (A + A.T) / 2
    np.fill_diagonal(A, 0)
    
    # Propagate through layers
    for _ in range(num_layers):
        h = message_passing_layer(h, A)
    
    return h

if __name__ == "__main__":
    graph = graph_representation(num_nodes=5)
    print(f"Graph: {graph['num_nodes']} nodes, {graph['num_edges']} edges")
    
    h = node_classification_demo(num_nodes=5)
    print(f"Node embeddings shape: {h.shape}")
