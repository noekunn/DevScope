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
import plotly.graph_objects as go
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="Codebase X-Ray - DevScope",
    page_icon="🔬",
    layout="wide"
)

# Apply shared warm theme
from src.dashboard.components.theme import inject_theme
inject_theme()

# Page-specific styles
st.markdown("""
<style>
    .language-badge {
        display: inline-block; padding: 0.5rem 1rem; border-radius: 99px;
        font-weight: 600; margin: 0.25rem; font-size: 0.85rem;
    }
    .lang-python { background: #fdf2f8; color: #ec4899; }
    .lang-javascript { background: #fff7ed; color: #ea580c; }
    .lang-typescript { background: #eff6ff; color: #2563eb; }
    .lang-java { background: #f0fdf4; color: #16a34a; }
    .lang-go { background: #f0fdf4; color: #16a34a; }
    .lang-rust { background: #fef2f2; color: #dc2626; }
    .module-card {
        background: #ffffff; border-radius: 16px; padding: 1.5rem;
        border-left: 4px solid #ec4899; margin-bottom: 1rem;
        border: 1px solid #e8e5df; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .module-name { font-size: 1.2rem; font-weight: 700; color: #1c1917; margin-bottom: 0.5rem; }
    .module-role {
        display: inline-block; background: linear-gradient(135deg, #ec4899, #f97316);
        color: white; padding: 0.2rem 0.7rem; border-radius: 99px;
        font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem;
    }
    .module-description { color: #57534e; font-size: 0.95rem; line-height: 1.6; }
    .module-purpose { color: #78716c; font-size: 0.85rem; font-style: italic; }
</style>
""", unsafe_allow_html=True)


def render_tech_stack(analysis_results: Dict[str, Any]):
    """Render tech stack section with language detection."""
    st.markdown('<div class="section-header">🔧 Tech Stack</div>', unsafe_allow_html=True)

    languages = {}
    complexity_data = analysis_results.get('complexity', {})
    files = complexity_data.get('files', [])

    for file_data in files:
        lang = file_data.get('language', 'Unknown')
        if lang and lang != 'Unknown':
            languages[lang] = languages.get(lang, 0) + 1

    if not languages and complexity_data.get('total_files', 0) > 0:
        languages['Python'] = complexity_data['total_files']

    if len(languages) == 0:
        st.info("No languages detected in the analysis")
        return

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

    try:
        from src.graph import Neo4jClient
        neo4j_client = Neo4jClient.get_instance()
        modules = []

        if neo4j_client.connected and neo4j_client.driver:
            query = """
            MATCH (m:Module)
            RETURN m.name as name, m.purpose as purpose,
                   m.architectural_role as role, m.patterns as patterns,
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
            _render_fallback_architecture(graph_summary)

    except Exception:
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

    sorted_files = sorted(files, key=lambda x: x.get('max_complexity', x.get('complexity', 0)), reverse=True)[:20]
    file_names = [f['path'].replace('\\\\', '/').split('/')[-1] for f in sorted_files]
    complexities = [f.get('max_complexity', f.get('complexity', 0)) for f in sorted_files]

    colors = []
    for c in complexities:
        if c < 5:
            colors.append('#16a34a')
        elif c < 10:
            colors.append('#ea580c')
        else:
            colors.append('#dc2626')

    fig = go.Figure(data=[
        go.Bar(
            x=complexities, y=file_names, orientation='h',
            marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.1)', width=1)),
            text=complexities, textposition='auto',
            textfont=dict(color='#1c1917')
        )
    ])

    fig.update_layout(
        title=dict(text="Top 20 Most Complex Files", font=dict(color='#1c1917')),
        xaxis_title="Cyclomatic Complexity",
        yaxis_title="File",
        height=600,
        plot_bgcolor='#ffffff',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1c1917', family='Inter'),
        xaxis=dict(gridcolor='#e8e5df'),
        yaxis=dict(gridcolor='#e8e5df'),
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

    if health_score >= 80:
        rating, color = "Excellent", "#16a34a"
    elif health_score >= 60:
        rating, color = "Good", "#2563eb"
    elif health_score >= 40:
        rating, color = "Fair", "#ea580c"
    else:
        rating, color = "Needs Improvement", "#dc2626"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Codebase Health", 'font': {'size': 24, 'color': '#1c1917'}},
        number={'font': {'size': 60, 'color': color}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#78716c'},
            'bar': {'color': color},
            'bgcolor': '#f5f4ef',
            'borderwidth': 2,
            'bordercolor': '#e8e5df',
            'steps': [
                {'range': [0, 40], 'color': 'rgba(220,38,38,0.1)'},
                {'range': [40, 60], 'color': 'rgba(234,88,12,0.1)'},
                {'range': [60, 80], 'color': 'rgba(37,99,235,0.1)'},
                {'range': [80, 100], 'color': 'rgba(22,163,74,0.1)'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': health_score
            }
        }
    ))

    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#1c1917', 'family': 'Inter'},
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"""
        <div class="health-card">
            <div class="health-rating">{rating}</div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main Codebase X-Ray page."""
    st.markdown('<div class="gradient-header">🔬 Codebase X-Ray</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Comprehensive architecture overview and health analysis</div>', unsafe_allow_html=True)

    if not st.session_state.get('analysis_complete', False):
        st.markdown("""
        <div class="info-message">
            <div class="info-icon">🔍</div>
            <div class="info-text">No analysis data available</div>
            <p style="color: #78716c;">Please run the analysis from the Home page first.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    analysis_results = st.session_state.get('analysis_results', {})
    graph_summary = st.session_state.get('graph_summary', {})

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
