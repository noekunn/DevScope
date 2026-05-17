"""
Codebase X-Ray - Architecture Overview Page.

Provides a comprehensive visual overview of the codebase architecture:
- Tech stack detection
- Module clusters with semantic descriptions
- Dependency summary
- Complexity heatmap
- Health score gauge
"""


import sys
from pathlib import Path

# Add project root to path for absolute imports
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="Codebase X-Ray - DevScope",
    page_icon="🔬",
    layout="wide"
)

# Premium dark theme CSS
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, #0a0f1c 0%, #1a1f2e 100%);
    }
    
    /* Gradient headers */
    .gradient-header {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    .section-header {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #475569;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 12px rgba(99, 102, 241, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    /* Module cards */
    .module-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #6366f1;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .module-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    .module-role {
        display: inline-block;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .module-description {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    
    .module-purpose {
        color: #94a3b8;
        font-size: 0.85rem;
        font-style: italic;
    }
    
    /* Language badges */
    .language-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    
    .lang-python { background: linear-gradient(135deg, #3776ab 0%, #ffd43b 100%); color: white; }
    .lang-javascript { background: linear-gradient(135deg, #f7df1e 0%, #f0db4f 100%); color: #323330; }
    .lang-typescript { background: linear-gradient(135deg, #3178c6 0%, #235a97 100%); color: white; }
    .lang-java { background: linear-gradient(135deg, #007396 0%, #f89820 100%); color: white; }
    .lang-go { background: linear-gradient(135deg, #00add8 0%, #5dc9e2 100%); color: white; }
    .lang-rust { background: linear-gradient(135deg, #ce422b 0%, #f74c00 100%); color: white; }
    
    /* Health gauge */
    .health-container {
        text-align: center;
        padding: 2rem;
    }
    
    .health-score {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .health-rating {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-top: 0.5rem;
    }
    
    /* Info message */
    .info-message {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-left: 4px solid #6366f1;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
    }
    
    .info-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .info-text {
        color: #cbd5e1;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def render_tech_stack(analysis_results: Dict[str, Any]):
    """Render tech stack section with language detection."""
    st.markdown('<div class="section-header">🔧 Tech Stack</div>', unsafe_allow_html=True)
    
    # Get language statistics from per-file data
    languages = {}
    complexity_data = analysis_results.get('complexity', {})
    files = complexity_data.get('files', [])
    
    for file_data in files:
        lang = file_data.get('language', 'Unknown')
        if lang and lang != 'Unknown':
            languages[lang] = languages.get(lang, 0) + 1
    
    # Fallback: if no per-file data, infer from total_files
    if not languages and complexity_data.get('total_files', 0) > 0:
        languages['Python'] = complexity_data['total_files']
    
    if len(languages) == 0:
        st.info("No languages detected in the analysis")
        return
    
    # Display as metric cards
    cols = st.columns(max(1, min(len(languages), 4)))
    for idx, (lang, count) in enumerate(sorted(languages.items(), key=lambda x: x[1], reverse=True)):
        with cols[idx % len(cols)]:
            lang_class = f"lang-{lang.lower()}"
            st.markdown(f"""
            <div class="metric-card">
                <div class="language-badge {lang_class}">{lang}</div>
                <div class="metric-value">{count}</div>
                <div class="metric-label">Files</div>
            </div>
            """, unsafe_allow_html=True)


def render_architecture_overview(graph_summary: Dict[str, Any]):
    """Render architecture overview with module clusters."""
    st.markdown('<div class="section-header">🏗️ Architecture Overview</div>', unsafe_allow_html=True)
    
    # Try to get enriched modules from Neo4j
    try:
        from src.graph import Neo4jClient
        neo4j_client = Neo4jClient.get_instance()
        modules = []
        
        if neo4j_client.connected and neo4j_client.driver:
            query = """
            MATCH (m:Module)
            RETURN m.name as name,
                   m.purpose as purpose,
                   m.architectural_role as role,
                   m.patterns as patterns,
                   m.priority as priority
            ORDER BY m.priority DESC
            """
            
            with neo4j_client.driver.session() as session:
                result = session.run(query)
                modules = [dict(record) for record in result]
        
        if modules:
            roles = {}
            for module in modules:
                role = module.get('role', 'Unknown')
                if role not in roles:
                    roles[role] = []
                roles[role].append(module)
            
            for role, role_modules in roles.items():
                st.markdown(f"### {role}")
                for module in role_modules:
                    name = module.get('name', 'Unknown')
                    purpose = module.get('purpose', 'No description available')
                    patterns = module.get('patterns', '')
                    
                    st.markdown(f"""
                    <div class="module-card">
                        <div class="module-name">{name}</div>
                        <div class="module-role">{role}</div>
                        <div class="module-description">{purpose}</div>
                        {f'<div class="module-purpose">Patterns: {patterns}</div>' if patterns else ''}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Show fallback with graph_summary data
            _render_fallback_architecture(graph_summary)
            
    except Exception as e:
        _render_fallback_architecture(graph_summary)


def _render_fallback_architecture(graph_summary: Dict[str, Any]):
    """Render architecture using graph summary data (fallback)."""
    nodes = graph_summary.get('nodes_created', 0)
    rels = graph_summary.get('relationships_created', 0)
    modules = graph_summary.get('modules_detected', 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{nodes}</div>
            <div class="metric-label">Graph Nodes</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{rels}</div>
            <div class="metric-label">Relationships</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{modules}</div>
            <div class="metric-label">Modules Detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show communities if available
    communities = graph_summary.get('communities', [])
    if communities:
        st.markdown("**Detected Module Clusters:**")
        for idx, community in enumerate(communities[:5], 1):
            size = community.get('size', 0)
            members = community.get('members', [])
            preview = ', '.join([m.split('\\\\')[-1].split('/')[-1] for m in members[:3]])
            st.markdown(f"""
            <div class="module-card">
                <div class="module-name">Module {idx}</div>
                <div class="module-role">Cluster ({size} files)</div>
                <div class="module-description">{preview}{'...' if len(members) > 3 else ''}</div>
            </div>
            """, unsafe_allow_html=True)


def render_dependency_summary(analysis_results: Dict[str, Any]):
    """Render dependency summary with key metrics."""
    st.markdown('<div class="section-header">🔗 Dependency Summary</div>', unsafe_allow_html=True)
    
    deps = analysis_results.get('dependencies', {})
    import_count = deps.get('import_count', 0)
    call_count = deps.get('call_count', 0)
    
    imports = deps.get('imports', [])
    external_deps = set()
    for imp in imports:
        target = imp.get('target', '')
        if target and not target.startswith('.') and not target.startswith('/'):
            external_deps.add(target.split('.')[0])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{import_count}</div>
            <div class="metric-label">Total Imports</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{call_count}</div>
            <div class="metric-label">Function Calls</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(external_deps)}</div>
            <div class="metric-label">External Dependencies</div>
        </div>
        """, unsafe_allow_html=True)


def render_complexity_heatmap(analysis_results: Dict[str, Any]):
    """Render complexity heatmap with color coding."""
    st.markdown('<div class="section-header">📊 Complexity Heatmap</div>', unsafe_allow_html=True)
    
    complexity_data = analysis_results.get('complexity', {})
    files = complexity_data.get('files', [])
    
    if not files:
        st.info("No complexity data available.")
        return
    
    # Sort by complexity (use max_complexity for more meaningful ranking)
    sorted_files = sorted(files, key=lambda x: x.get('max_complexity', x.get('complexity', 0)), reverse=True)[:20]
    
    # Prepare data
    file_names = [f['path'].replace('\\\\', '/').split('/')[-1] for f in sorted_files]
    complexities = [f.get('max_complexity', f.get('complexity', 0)) for f in sorted_files]
    
    # Color code
    colors = []
    for c in complexities:
        if c < 5:
            colors.append('#10b981')
        elif c < 10:
            colors.append('#f59e0b')
        else:
            colors.append('#ef4444')
    
    fig = go.Figure(data=[
        go.Bar(
            x=complexities,
            y=file_names,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
            ),
            text=complexities,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Top 20 Most Complex Files",
        xaxis_title="Cyclomatic Complexity",
        yaxis_title="File",
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Low** (< 5): Easy to maintain")
    with col2:
        st.markdown("🟡 **Medium** (5-10): Moderate complexity")
    with col3:
        st.markdown("🔴 **High** (> 10): Needs refactoring")


def render_health_score(analysis_results: Dict[str, Any]):
    """Render health score gauge."""
    st.markdown('<div class="section-header">💚 Health Score</div>', unsafe_allow_html=True)
    
    health_score = analysis_results.get('health_score', 0)
    
    # Determine rating
    if health_score >= 80:
        rating = "Excellent"
        color = "#10b981"
    elif health_score >= 60:
        rating = "Good"
        color = "#3b82f6"
    elif health_score >= 40:
        rating = "Fair"
        color = "#f59e0b"
    else:
        rating = "Needs Improvement"
        color = "#ef4444"
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Codebase Health", 'font': {'size': 24, 'color': '#e2e8f0'}},
        number={'font': {'size': 60, 'color': color}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#e2e8f0"},
            'bar': {'color': color},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 2,
            'bordercolor': "#475569",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [40, 60], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [60, 80], 'color': 'rgba(59, 130, 246, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': health_score
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#e2e8f0", 'family': "Arial"},
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"""
        <div class="health-container">
            <div class="health-rating">{rating}</div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main Codebase X-Ray page."""
    st.markdown('<div class="gradient-header">🔬 Codebase X-Ray</div>', unsafe_allow_html=True)
    st.markdown("**Comprehensive architecture overview and health analysis**")
    
    # Debug: Show session state keys
    # st.write("Session state keys:", list(st.session_state.keys()))
    
    # Check if analysis has been run
    if not st.session_state.get('analysis_complete', False):
        st.markdown("""
        <div class="info-message">
            <div class="info-icon">🔍</div>
            <div class="info-text">No analysis data available</div>
            <p style="color: #94a3b8;">Please run the analysis from the Home page first to see the codebase overview.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    analysis_results = st.session_state.get('analysis_results', {})
    graph_summary = st.session_state.get('graph_summary', {})
    
    # Render sections
    render_tech_stack(analysis_results)
    
    st.markdown("---")
    render_architecture_overview(graph_summary)
    
    st.markdown("---")
    render_dependency_summary(analysis_results)
    
    st.markdown("---")
    render_complexity_heatmap(analysis_results)
    
    st.markdown("---")
    render_health_score(analysis_results)


if __name__ == "__main__":
    main()

# Made with Bob
