"""
Graph Visualization Component — Pyvis rendering for knowledge graph.
"""
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx
from typing import Dict, Any, Optional
import tempfile
import os


def render_graph(G: nx.DiGraph, height: str = "600px", highlight_mode: str = "cluster",
                 selected_node: Optional[str] = None) -> None:
    """
    Render a NetworkX graph using Pyvis inside Streamlit.
    
    Args:
        G: NetworkX DiGraph to render.
        height: Height of the visualization.
        highlight_mode: One of 'cluster', 'critical', 'impact'.
        selected_node: Node to highlight for impact view.
    """
    if len(G.nodes) == 0:
        st.info("No graph data to display.")
        return
    
    net = Network(height=height, width="100%", directed=True, bgcolor="#0a0f1c", font_color="#e2e8f0")
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=100)
    
    # Get PageRank for sizing
    try:
        pagerank = nx.pagerank(G)
    except Exception:
        pagerank = {n: 1.0 / len(G) for n in G.nodes}
    
    # Get communities for coloring
    communities = {}
    try:
        from networkx.algorithms.community import louvain_communities
        comms = louvain_communities(G.to_undirected())
        for idx, comm in enumerate(comms):
            for node in comm:
                communities[node] = idx
    except Exception:
        pass
    
    # Color palette
    colors = ['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b',
              '#ef4444', '#3b82f6', '#10b981', '#f97316', '#06b6d4']
    
    # Add nodes
    for node in G.nodes:
        pr_score = pagerank.get(node, 0)
        size = max(10, min(50, pr_score * 5000))
        label = os.path.basename(str(node))
        
        if highlight_mode == 'cluster':
            comm_id = communities.get(node, 0)
            color = colors[comm_id % len(colors)]
        elif highlight_mode == 'critical':
            color = '#ef4444' if pr_score > 0.02 else '#6366f1'
        else:
            color = '#6366f1'
        
        net.add_node(str(node), label=label, size=size, color=color,
                     title=f"{node}\nPageRank: {pr_score:.4f}")
    
    # Add edges
    for source, target in G.edges:
        net.add_edge(str(source), str(target), color='rgba(255,255,255,0.2)')
    
    # Render
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as html_file:
            html_content = html_file.read()
        components.html(html_content, height=int(height.replace('px', '')) + 20, scrolling=True)
        os.unlink(f.name)


# Made with Bob
