#set page(margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm))
#set text(font: "New Computer Modern", size: 11pt)

#import "generated/formulas.typ": *

= Graph Neural Networks: Message Passing & Attention

_Neural networks on graph-structured data_

== 1. Introduction
Graph Neural Networks (GNNs) extend deep learning to non-Euclidean domains where data has graph structure (social networks, molecules, knowledge graphs). Information propagates via message passing.

== 2. Graph Representation
Graphs comprise nodes (entities) and edges (relationships):

#figure(
  align(center, $G = (V, E)$),
  caption: [Graph structure (from model.py:15)]
)

Adjacency matrix A encodes connectivity: A[i,j] = 1 if nodes i and j are connected.

== 3. Node Features
Each node has a feature vector:

#figure(
  align(center, $h_i in RR^d$),
  caption: [Node feature vector (from model.py:30)]
)

d is feature dimension. Features can be learned or provided (e.g., node labels, attributes).

== 4. Message Passing
Information flows between neighbors:

#figure(
  align(center, $m_{i ← j} = W * h_j$),
  caption: [Message from neighbor j to i (from model.py:45)]
)

Where W is a learned weight matrix. Messages aggregate to update node state.

== 5. Aggregation
Neighbors' messages combine via aggregation:

#figure(
  align(center, $m_i^"agg" = Σ_{j ∈ N(i)} m_{i←j}$),
  caption: [Message aggregation (from model.py:50)]
)

Common aggregation: sum, mean, max. Order-invariant to handle variable neighborhood sizes.

== 6. Node Update
Aggregated messages update node representation:

#figure(
  align(center, $h_i^"new" = σ(W_{"self"} h_i + m_i^"agg")$),
  caption: [Node update (from model.py:60)]
)

σ is activation (ReLU, etc.). Combines node's own feature with neighbor information.

== 7. Multi-Layer Propagation
Stacking layers increases receptive field. L layers → each node sees neighbors up to distance L:

#figure(
  align(center, $"receptive field" = L$),
  caption: [Receptive field depth (from model.py:70)]
)

Deeper networks capture longer-range dependencies.

== 8. Attention Mechanisms
Attention weights modulate message importance:

#figure(
  align(center, $α_{"ij"} = "softmax"_j(a(h_i, h_j))$),
  caption: [Attention weights (from model.py:85)]
)

Where a is a learned attention function. Important neighbors get higher weights.

== 9. Node Classification
Supervised task: predict node labels given graph structure and features:

#figure(
  align(center, $ŷ_i = "argmax"(h_i^"final")$),
  caption: [Node classification (from model.py:95)]
)

GNNs learn features that respect graph structure, outperforming node-feature-only baselines.

== 10. Conclusion
GNNs extend neural networks to graphs by passing messages along edges. Attention mechanisms weight neighbor importance. Applications span molecular properties, social recommendation, and knowledge graph completion. Graph structure inductive bias improves generalization and reduces parameters vs. fully-connected networks.

---

#set text(size: 9pt, fill: gray)

_Paper generated from model.py and main.typ. All formulas traced to source code._
