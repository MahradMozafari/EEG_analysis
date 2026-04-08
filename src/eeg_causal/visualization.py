from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

def plot_connectivity_matrix(connectivity, roi_names, title="Connectivity Matrix", 
                            threshold=0.0, save_path=None):
    """
    Plot connectivity matrix as heatmap
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Threshold (optional)
    conn_thresh = connectivity.copy()
    if threshold > 0:
        conn_thresh[conn_thresh < threshold] = 0
    
    sns.heatmap(
        conn_thresh,
        xticklabels=roi_names,
        yticklabels=roi_names,
        cmap='YlOrRd',
        vmin=0,
        vmax=np.max(connectivity),
        annot=True,
        fmt=".2f",
        cbar_kws={'label': 'Connection Strength'},
        ax=ax
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Target ROI →', fontsize=12)
    ax.set_ylabel('← Source ROI', fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_network_graph(connectivity, roi_names, title="Connectivity Network", 
                       threshold=0.5, save_path=None):
    """
    Plot connectivity as directed network graph
    """
    # Create directed graph
    G = nx.DiGraph()
    G.add_nodes_from(roi_names)
    
    # Add edges above threshold
    for i, src in enumerate(roi_names):
        for j, tgt in enumerate(roi_names):
            weight = connectivity[i, j]
            if weight > threshold and i != j:
                G.add_edge(src, tgt, weight=float(weight))
    
    # Check whether edges exist
    if G.number_of_edges() == 0:
        print(f"⚠️ No edges above threshold ({threshold}) in {title}")
        return
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Draw
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color='lightblue',
        node_size=2500,
        alpha=0.9,
        ax=ax
    )
    
    # Edges
    edges = list(G.edges())
    weights = [G[u][v]['weight'] for u, v in edges]
    
    # Normalize weights for visualization
    max_weight = max(weights) if weights else 1
    norm_weights = [w/max_weight for w in weights]
    
    nx.draw_networkx_edges(
        G, pos,
        edgelist=edges,
        width=[w*5 + 1 for w in norm_weights],  # +1 for visibility
        alpha=0.6,
        edge_color=weights,
        edge_cmap=plt.cm.YlOrRd,
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        ax=ax
    )
    
    # Labels
    nx.draw_networkx_labels(
        G, pos,
        font_size=10,
        font_weight='bold',
        ax=ax
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
    
    print(f"   📊 Network stats: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")


print("✅ Visualization functions defined")
