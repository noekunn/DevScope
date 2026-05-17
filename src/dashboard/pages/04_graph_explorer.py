"""
Graph Explorer - Interactive Knowledge Graph Visualization

Visualizes the codebase knowledge graph with interactive controls and highlight modes.
"""

import streamlit as st
import sys
from pathlib import Path
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.graph import Neo4jClient

# Page configuration
st.set_page_config(
    page_title="Graph Explorer - DevScope",
    page_icon="🕸️",
    layout="wide"
)

# Apply shared warm theme
from src.dashboard.components.theme import inject_theme
inject_theme()

# Initialize Neo4j client
@st.cache_resource
def get_neo4j_client():
    return Neo4jClient.get_instance()

def get_graph_data():
    """Fetch graph data from Neo4j."""
    client = get_neo4j_client()
    
    if client.fallback_mode:
        # Use NetworkX fallback
        nodes = []
        edges = []
        for node in client.nx_graph.nodes():
            node_data = client.nx_graph.nodes[node]
            nodes.append({
                'id': node,
                'label': node.split('/')[-1] if '/' in node else node,
                'title': node,
                **node_data
            })
        
        for source, target in client.nx_graph.edges():
            edge_data = client.nx_graph.edges[source, target]
            edges.append({
                'from': source,
                'to': target,
                **edge_data
            })
        
        return nodes, edges
    
    # Fetch from Neo4j
    try:
        with client.driver.session() as session:
            # Get nodes
            node_result = session.run("""
                MATCH (n:CodeElement)
                RETURN elementId(n) as id, 
                       n.path as path,
                       n.name as name,
                       n.type as type,
                       n.complexity as complexity,
                       n.language as language,
                       n.lines as lines
                LIMIT 500
            """)
            
            nodes = []
            for record in node_result:
                node_id = record['id']
                label = record['path'] or record['name'] or 'Unknown'
                label = label.split('/')[-1] if '/' in label else label
                
                nodes.append({
                    'id': node_id,
                    'label': label,
                    'title': record['path'] or record['name'],
                    'type': record['type'],
                    'complexity': record['complexity'] or 0,
                    'language': record['language'],
                    'lines': record['lines'] or 0
                })
            
            # Get edges
            edge_result = session.run("""
                MATCH (n:CodeElement)-[r]->(m:CodeElement)
                RETURN elementId(n) as from,
                       elementId(m) as to,
                       type(r) as rel_type
                LIMIT 1000
            """)
            
            edges = []
            for record in edge_result:
                edges.append({
                    'from': record['from'],
                    'to': record['to'],
                    'type': record['rel_type']
                })
            
            return nodes, edges
            
    except Exception as e:
        st.error(f"Error fetching graph data: {e}")
        return [], []

def create_pyvis_graph(nodes, edges, highlight_mode, selected_file=None, 
                      file_type_filter=None, complexity_filter=None):
    """Create Pyvis network graph with styling."""
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#f5f4ef",
        font_color="#1c1917",
        directed=True
    )
    
    # Configure physics
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 95,
                "springConstant": 0.04
            },
            "stabilization": {
                "iterations": 150
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100
        }
    }
    """)
    
    # Get PageRank scores for critical path mode
    pagerank_scores = {}
    if highlight_mode == "Critical Path":
        client = get_neo4j_client()
        try:
            pr_results = client.run_pagerank(top_n=50)
            for result in pr_results:
                node_id = result.get('path') or result.get('name')
                if node_id:
                    pagerank_scores[node_id] = result.get('score', 0)
        except:
            pass
    
    # Get communities for cluster view
    communities = {}
    if highlight_mode == "Cluster View":
        client = get_neo4j_client()
        try:
            comm_results = client.detect_communities()
            for i, comm in enumerate(comm_results):
                for member in comm.get('members', []):
                    communities[member] = i
        except:
            pass
    
    # Get impact radius for impact view
    impacted_nodes = set()
    if highlight_mode == "Impact View" and selected_file:
        client = get_neo4j_client()
        try:
            impacted = client.find_impact_radius(selected_file, depth=3)
            impacted_nodes = set(impacted)
        except:
            pass
    
    # Filter nodes
    filtered_nodes = nodes
    if file_type_filter and file_type_filter != "All":
        filtered_nodes = [n for n in nodes if n.get('language') == file_type_filter.lower()]
    
    if complexity_filter:
        min_complexity, max_complexity = complexity_filter
        filtered_nodes = [n for n in filtered_nodes 
                         if min_complexity <= n.get('complexity', 0) <= max_complexity]
    
    # Add nodes with styling
    node_ids = set()
    for node in filtered_nodes:
        node_id = node['id']
        node_ids.add(node_id)
        
        # Determine color based on highlight mode
        color = "#ec4899"  # Default pink
        size = 20
        
        if highlight_mode == "Critical Path":
            title = node.get('title', '')
            if title in pagerank_scores:
                score = pagerank_scores[title]
                if score > 0.01:
                    color = "#ef4444"  # Red for critical
                    size = 30
                elif score > 0.005:
                    color = "#f59e0b"  # Orange for important
                    size = 25
        
        elif highlight_mode == "Cluster View":
            title = node.get('title', '')
            if title in communities:
                comm_id = communities[title]
                colors = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#3b82f6"]
                color = colors[comm_id % len(colors)]
        
        elif highlight_mode == "Impact View":
            title = node.get('title', '')
            if title == selected_file:
                color = "#ef4444"  # Red for selected
                size = 35
            elif title in impacted_nodes:
                color = "#f59e0b"  # Orange for impacted
                size = 25
        
        # Size by complexity
        complexity = node.get('complexity', 0)
        if complexity > 10:
            size = max(size, 30)
        elif complexity > 5:
            size = max(size, 25)
        
        # Create tooltip
        tooltip = f"""
        <b>{node.get('label', 'Unknown')}</b><br>
        Type: {node.get('type', 'unknown')}<br>
        Complexity: {complexity}<br>
        Lines: {node.get('lines', 0)}<br>
        Language: {node.get('language', 'unknown')}
        """
        
        net.add_node(
            node_id,
            label=node.get('label', 'Unknown'),
            title=tooltip,
            color=color,
            size=size
        )
    
    # Add edges
    for edge in edges:
        if edge['from'] in node_ids and edge['to'] in node_ids:
            edge_color = "#4b5563"  # Gray
            
            # Highlight edges in impact view
            if highlight_mode == "Impact View" and selected_file:
                if edge['from'] in impacted_nodes or edge['to'] in impacted_nodes:
                    edge_color = "#f59e0b"
            
            net.add_edge(
                edge['from'],
                edge['to'],
                color=edge_color,
                arrows="to"
            )
    
    return net

def render_sidebar(nodes, edges):
    """Render sidebar with statistics and controls."""
    st.sidebar.markdown("## 🕸️ Graph Explorer")
    st.sidebar.markdown("---")
    
    # Statistics
    st.sidebar.markdown("### 📊 Graph Statistics")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Nodes", len(nodes))
        st.metric("Edges", len(edges))
    
    with col2:
        # Calculate clusters
        client = get_neo4j_client()
        try:
            communities = client.detect_communities()
            st.metric("Clusters", len(communities))
        except:
            st.metric("Clusters", "N/A")
        
        # Calculate cycles
        try:
            cycles = client.detect_cycles()
            st.metric("Cycles", len(cycles))
        except:
            st.metric("Cycles", "N/A")
    
    st.sidebar.markdown("---")
    
    # Filters
    st.sidebar.markdown("### 🎛️ Filters")
    
    # File type filter
    languages = set(n.get('language', 'unknown') for n in nodes)
    languages = sorted([l for l in languages if l])
    file_type = st.sidebar.selectbox(
        "File Type",
        ["All"] + [l.title() for l in languages]
    )
    
    # Complexity filter
    complexity_range = st.sidebar.slider(
        "Complexity Range",
        min_value=0,
        max_value=50,
        value=(0, 50)
    )
    
    st.sidebar.markdown("---")
    
    # Highlight modes
    st.sidebar.markdown("### 🎨 Highlight Mode")
    highlight_mode = st.sidebar.radio(
        "Select mode",
        ["Default", "Critical Path", "Cluster View", "Impact View"]
    )
    
    selected_file = None
    if highlight_mode == "Impact View":
        file_options = [n.get('title', n.get('label', '')) for n in nodes if n.get('type') == 'file']
        selected_file = st.sidebar.selectbox(
            "Select file to analyze impact",
            [""] + sorted(file_options)
        )
    
    return file_type, complexity_range, highlight_mode, selected_file

def main():
    """Main graph explorer page."""
    st.title("🕸️ Knowledge Graph Explorer")
    st.markdown("Interactive visualization of your codebase structure and dependencies")
    
    # Debug: Show session state keys
    # st.write("Session state keys:", list(st.session_state.keys()))
    
    # Check if analysis has been run
    if not st.session_state.get('analysis_complete', False):
        st.warning("⚠️ Please run the analysis first from the main page")
        st.info("👈 Go to the main page and click 'Analyze Codebase'")
        return
    
    # Fetch graph data
    with st.spinner("Loading graph data..."):
        nodes, edges = get_graph_data()
    
    if not nodes:
        st.error("No graph data available. Please ensure the analysis completed successfully.")
        return
    
    # Render sidebar and get controls
    file_type, complexity_range, highlight_mode, selected_file = render_sidebar(nodes, edges)
    
    # Create and display graph
    st.markdown("### Graph Visualization")
    
    # Info about current mode
    if highlight_mode == "Critical Path":
        st.info("🔴 Red nodes are critical files (high PageRank)")
    elif highlight_mode == "Cluster View":
        st.info("🎨 Colors represent different modules/clusters")
    elif highlight_mode == "Impact View" and selected_file:
        st.info(f"🎯 Showing impact radius for: {selected_file}")
    
    # Generate graph
    with st.spinner("Generating visualization..."):
        net = create_pyvis_graph(
            nodes, edges, highlight_mode, selected_file,
            file_type if file_type != "All" else None,
            complexity_range
        )
        
        # Save to temp file and display
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            net.save_graph(f.name)
            with open(f.name, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
        
        components.html(html_content, height=750, scrolling=True)
    
    # Legend
    st.markdown("---")
    st.markdown("### 📖 Legend")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Node Colors:**
        - 🔵 Default (Indigo)
        - 🔴 Critical (Red)
        - 🟠 Important (Orange)
        - 🟣 Cluster colors (various)
        """)
    
    with col2:
        st.markdown("""
        **Node Size:**
        - Larger = Higher complexity
        - Smaller = Lower complexity
        """)
    
    with col3:
        st.markdown("""
        **Interactions:**
        - Click & drag to move nodes
        - Scroll to zoom
        - Hover for details
        """)

if __name__ == "__main__":
    main()

# Made with Bob
