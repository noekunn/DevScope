"""
DevScope - Intelligent Codebase Onboarding Dashboard

Main Streamlit application with premium warm theme inspired by weco.ai.
"""

import streamlit as st
import time
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analyzers import DependencyAnalyzer, ComplexityAnalyzer
from src.graph import Neo4jClient, GraphBuilder
from src.semantic import GraniteClient, SemanticEnricher
from src.generators import OnboardingGenerator

# Import git for cloning
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

# Page configuration
st.set_page_config(
    layout="wide",
    page_title="DevScope - Intelligent Codebase Onboarding",
    page_icon="🔍",
    initial_sidebar_state="expanded"
)

# Premium warm theme CSS (weco.ai inspired)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Warm cream background */
    .stApp {
        background-color: #f5f4ef !important;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e8e5df;
    }
    [data-testid="stSidebar"] * {
        color: #1c1917 !important;
    }

    /* Hide ugly default page nav */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Custom sidebar nav links */
    .sidebar-nav { margin: 0.5rem 0; }
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.7rem 1rem;
        border-radius: 12px;
        margin: 0.25rem 0;
        color: #57534e !important;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        cursor: pointer;
        text-decoration: none !important;
    }
    .sidebar-nav-item:hover {
        background: linear-gradient(135deg, #fdf2f8, #fff7ed);
        color: #1c1917 !important;
    }
    .sidebar-nav-item.active {
        background: linear-gradient(135deg, #fdf2f8, #fff7ed);
        color: #ec4899 !important;
        font-weight: 600;
        border: 1px solid #fce7f3;
    }
    .sidebar-nav-icon {
        font-size: 1.1rem;
        width: 1.5rem;
        text-align: center;
    }

    /* Style page_link buttons to look like nav items */
    [data-testid="stSidebar"] .stPageLink > a {
        background: transparent !important;
        border: none !important;
        padding: 0.7rem 1rem !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        color: #57534e !important;
        text-decoration: none !important;
        display: block;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stPageLink > a:hover {
        background: linear-gradient(135deg, #fdf2f8, #fff7ed) !important;
        color: #1c1917 !important;
    }

    /* All text dark */
    .stMarkdown, .stMarkdown p, .stMarkdown li, label, .stTextInput label {
        color: #1c1917 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1c1917 !important;
        font-family: 'Inter', sans-serif !important;
        -webkit-text-fill-color: #1c1917 !important;
        background: none !important;
        -webkit-background-clip: unset !important;
    }

    /* Hero title gradient override */
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        line-height: 1.1 !important;
        margin-bottom: 1rem !important;
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }

    .hero-sub {
        font-size: 1.3rem;
        color: #57534e !important;
        font-weight: 400;
        max-width: 600px;
    }

    /* Logo */
    .logo-box {
        text-align: center;
        padding: 1.5rem 1rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #fdf2f8, #fff7ed);
        border-radius: 16px;
        border: 1px solid #fce7f3;
    }
    .logo-name {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ec4899, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .logo-tag {
        color: #78716c !important;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }

    /* Cards */
    .wcard {
        background: #ffffff;
        border: 1px solid #e8e5df;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    .wcard:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        border-color: #d6d3d1;
    }
    .wcard h3 {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .wcard p {
        color: #78716c !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .wcard-link {
        color: #ec4899 !important;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 1rem;
        display: inline-block;
    }

    /* Style page_link buttons in main area to look like card links */
    .main .stPageLink > a {
        background: transparent !important;
        border: 1px solid #fce7f3 !important;
        border-radius: 12px !important;
        color: #ec4899 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1.2rem !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
    }
    .main .stPageLink > a:hover {
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        color: white !important;
        border-color: transparent !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(236,72,153,0.3) !important;
    }

    /* Feature chips */
    .chip {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 99px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .chip-pink { background: #fdf2f8; color: #ec4899; }
    .chip-orange { background: #fff7ed; color: #ea580c; }
    .chip-green { background: #f0fdf4; color: #16a34a; }
    .chip-blue { background: #eff6ff; color: #2563eb; }
    .chip-purple { background: #faf5ff; color: #9333ea; }

    /* Metric cards */
    .stat-card {
        background: #ffffff;
        border: 1px solid #e8e5df;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ec4899, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label {
        color: #78716c;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    /* Health gauge */
    .health-box {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #fdf2f8, #fff7ed);
        border-radius: 16px;
        border: 1px solid #fce7f3;
        margin: 0.5rem 0;
    }
    .health-num {
        font-size: 3rem;
        font-weight: 900;
    }
    .health-num.green { color: #16a34a; }
    .health-num.amber { color: #ea580c; }
    .health-num.red { color: #dc2626; }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(236,72,153,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(236,72,153,0.4) !important;
    }

    /* Input */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid #d6d3d1 !important;
        border-radius: 12px !important;
        color: #1c1917 !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #ec4899 !important;
        box-shadow: 0 0 0 3px rgba(236,72,153,0.1) !important;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #ec4899, #f97316) !important;
    }

    /* Divider */
    hr { border-color: #e8e5df !important; }

    /* Metric widget */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e8e5df;
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="stMetricValue"] {
        color: #1c1917 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #78716c !important;
    }

    /* Steps */
    .step-item {
        background: #ffffff;
        border: 1px solid #e8e5df;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .step-num {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ec4899, #f97316);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .step-text { color: #1c1917; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'repo_path' not in st.session_state:
    st.session_state.repo_path = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'health_score' not in st.session_state:
    st.session_state.health_score = 0


def run_full_analysis(repo_input: str):
    """Run the complete DevScope analysis pipeline."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    temp_dir = None

    try:
        # Handle GitHub URLs
        if repo_input.startswith(('https://', 'http://', 'git@')):
            if not GIT_AVAILABLE:
                st.error("❌ GitPython is not installed. Please install it: `pip install gitpython`")
                return False

            status_text.markdown("📥 **Cloning repository from GitHub...**")
            progress_bar.progress(5)

            try:
                temp_dir = tempfile.mkdtemp(prefix='devscope_')
                git.Repo.clone_from(repo_input, temp_dir, depth=1)
                repo_path = temp_dir
                st.success(f"✅ Repository cloned to: {temp_dir}")
                time.sleep(0.5)
            except Exception as e:
                st.error(f"❌ Failed to clone repository: {e}")
                if temp_dir and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                return False
        else:
            repo_path = repo_input
            if not Path(repo_path).exists():
                st.error(f"❌ Repository path does not exist: {repo_path}")
                return False

        # Step 1: Dependency Analysis
        status_text.markdown("🔍 **Step 1/5:** Analyzing dependencies...")
        progress_bar.progress(10)
        dep_analyzer = DependencyAnalyzer(repo_path)
        dep_results = dep_analyzer.analyze()
        time.sleep(0.5)
        progress_bar.progress(20)

        # Step 2: Complexity Analysis
        status_text.markdown("📊 **Step 2/5:** Analyzing code complexity...")
        complexity_analyzer = ComplexityAnalyzer(repo_path)
        complexity_results = complexity_analyzer.analyze()
        complexity_summary = complexity_analyzer.get_summary()
        st.session_state.health_score = complexity_summary['health_score']
        time.sleep(0.5)
        progress_bar.progress(40)

        # Step 3: Build Knowledge Graph
        status_text.markdown("🕸️ **Step 3/5:** Building knowledge graph...")
        graph_builder = GraphBuilder()
        graph_summary = graph_builder.build_graph(repo_path, clear_existing=True)
        time.sleep(0.5)
        progress_bar.progress(60)

        # Step 4: Semantic Enrichment
        status_text.markdown("🤖 **Step 4/5:** Adding AI-powered insights...")
        semantic_enricher = SemanticEnricher(repo_path)
        enrichment_summary = semantic_enricher.enrich_graph()
        time.sleep(0.5)
        progress_bar.progress(80)

        # Step 5: Generate Onboarding Guide
        status_text.markdown("📚 **Step 5/5:** Generating onboarding guides...")
        onboarding_gen = OnboardingGenerator(repo_path)
        guides = {
            'fullstack': onboarding_gen.generate_guide('fullstack'),
            'frontend': onboarding_gen.generate_guide('frontend'),
            'backend': onboarding_gen.generate_guide('backend'),
            'devops': onboarding_gen.generate_guide('devops')
        }
        time.sleep(0.5)
        progress_bar.progress(100)

        # Build per-file data with language info
        file_data = []
        for fm in complexity_results:
            ext = Path(fm['file']).suffix.lower()
            lang_map = {'.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                        '.jsx': 'JavaScript', '.tsx': 'TypeScript', '.java': 'Java',
                        '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.cpp': 'C++'}
            file_data.append({
                'path': fm['file'],
                'language': lang_map.get(ext, ext.lstrip('.').upper() if ext else 'Unknown'),
                'complexity': fm['avg_complexity'],
                'max_complexity': fm['max_complexity'],
                'total_lines': fm['total_lines'],
                'source_lines': fm['source_lines'],
                'function_count': fm['function_count'],
                'hotspot_count': fm['hotspot_count'],
                'functions': fm['functions']
            })

        st.session_state.analysis_results = {
            'dependencies': {
                'import_count': len(dep_results.get('imports', [])),
                'call_count': len(dep_results.get('calls', [])),
                'imports': dep_results.get('imports', []),
                'calls': dep_results.get('calls', [])
            },
            'complexity': {
                **complexity_summary,
                'files': file_data
            },
            'health_score': complexity_summary.get('health_score', 0)
        }
        st.session_state.graph_summary = graph_summary
        st.session_state.enrichment_summary = enrichment_summary
        st.session_state.guides = guides
        st.session_state.analyzed = True
        st.session_state.analysis_complete = True
        st.session_state.repo_path = repo_path
        st.session_state.temp_dir = temp_dir

        status_text.markdown("✅ **Analysis Complete!**")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()
        return True

    except Exception as e:
        status_text.empty()
        progress_bar.empty()
        st.error(f"❌ Analysis failed: {str(e)}")
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        return False


def render_sidebar():
    """Render the sidebar with logo and controls."""
    with st.sidebar:
        st.markdown("""
        <div class="logo-box">
            <div class="logo-name">🔍 DevScope</div>
            <div class="logo-tag">Intelligent Codebase Onboarding</div>
        </div>
        """, unsafe_allow_html=True)

        # Custom navigation
        st.markdown("#### Navigation")
        st.page_link("app.py", label="🏠  Home", use_container_width=True)
        st.page_link("pages/01_codebase_xray.py", label="🔬  Codebase X-Ray", use_container_width=True)
        st.page_link("pages/02_onboarding_hub.py", label="📚  Onboarding Hub", use_container_width=True)
        st.page_link("pages/03_modernization.py", label="🔄  Modernization", use_container_width=True)
        st.page_link("pages/04_graph_explorer.py", label="🕸️  Graph Explorer", use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📂 Repository")
        repo_input = st.text_input(
            "Enter repository path or GitHub URL",
            placeholder="/path/to/repo or https://github.com/user/repo",
            help="Provide a local path or GitHub repository URL"
        )

        if st.button("🚀 Analyze Codebase", use_container_width=True):
            if repo_input:
                with st.spinner("Analyzing..."):
                    success = run_full_analysis(repo_input)
                    if success:
                        st.success("✅ Analysis complete!")
                        st.balloons()
            else:
                st.warning("⚠️ Please enter a repository path")

        st.markdown("---")

        if st.session_state.analyzed:
            st.markdown("#### 💚 Codebase Health")
            score = st.session_state.health_score
            if score >= 75:
                cls = "green"
                rating = "Excellent"
            elif score >= 50:
                cls = "amber"
                rating = "Good"
            else:
                cls = "red"
                rating = "Needs Attention"

            st.markdown(f"""
            <div class="health-box">
                <div class="health-num {cls}">{score}</div>
                <div style="color:#78716c;font-size:0.95rem;">{rating}</div>
            </div>
            """, unsafe_allow_html=True)

            results = st.session_state.analysis_results
            graph_summary = st.session_state.get('graph_summary', {})
            enrichment_summary = st.session_state.get('enrichment_summary', {})
            if results:
                st.markdown("#### 📊 Quick Stats")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Files", graph_summary.get('files_analyzed', 0))
                    st.metric("Modules", enrichment_summary.get('modules_enriched', 0))
                with col2:
                    st.metric("Functions", results.get('complexity', {}).get('total_functions', 0))
                    st.metric("Hotspots", results.get('complexity', {}).get('hotspot_count', 0))


def render_main_area():
    """Render the main content area."""
    if not st.session_state.analyzed:
        # Hero
        st.markdown("""
        <div style="text-align:center;padding:4rem 0 2rem 0;">
            <div class="hero-title">Understand any codebase<br>in minutes, not weeks</div>
            <p class="hero-sub" style="margin:0 auto;">
                AI-powered analysis, knowledge graphs, and role-specific onboarding guides
                — all from a single GitHub URL.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Chips
        st.markdown("""
        <div style="text-align:center;margin-bottom:2rem;">
            <span class="chip chip-pink">AST Analysis</span>
            <span class="chip chip-orange">Knowledge Graph</span>
            <span class="chip chip-green">IBM Granite AI</span>
            <span class="chip chip-blue">Neo4j</span>
            <span class="chip chip-purple">Role-Based Guides</span>
        </div>
        """, unsafe_allow_html=True)

        # Feature cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="wcard">
                <h3>🔬 Deep Analysis</h3>
                <p>AST-based dependency analysis, cyclomatic complexity scoring, and hotspot detection across your entire codebase.</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="wcard">
                <h3>🤖 AI-Powered Insights</h3>
                <p>IBM Granite LLM generates semantic summaries, detects design patterns, and identifies modernization opportunities.</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="wcard">
                <h3>📚 Smart Onboarding</h3>
                <p>Role-specific guides help Frontend, Backend, Fullstack, and DevOps developers get productive on day one.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Steps
        st.markdown("### 🚀 Get Started")
        steps = [
            "Enter a GitHub URL or local path in the sidebar",
            "Click 'Analyze Codebase' — the 5-step pipeline runs automatically",
            "Explore X-Ray, Onboarding, Modernization, and Graph pages",
            "Download role-specific onboarding guides for your team"
        ]
        for i, step in enumerate(steps, 1):
            st.markdown(f"""
            <div class="step-item">
                <div class="step-num">{i}</div>
                <div class="step-text">{step}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Dashboard nav
        st.markdown("### 📊 Explore Your Codebase")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="wcard">
                <h3>🔬 Codebase X-Ray</h3>
                <p>Visualize dependencies, complexity hotspots, and tech stack.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/01_codebase_xray.py", label="→ Go to Codebase X-Ray", use_container_width=True)

            st.markdown("""
            <div class="wcard">
                <h3>🔄 Modernization</h3>
                <p>AI-detected refactoring opportunities and technical debt roadmap.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/03_modernization.py", label="→ Go to Modernization", use_container_width=True)
        with col2:
            st.markdown("""
            <div class="wcard">
                <h3>📚 Onboarding Hub</h3>
                <p>Role-specific guides and learning paths for new developers.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/02_onboarding_hub.py", label="→ Go to Onboarding Hub", use_container_width=True)

            st.markdown("""
            <div class="wcard">
                <h3>🕸️ Graph Explorer</h3>
                <p>Interactive knowledge graph with PageRank and community detection.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/04_graph_explorer.py", label="→ Go to Graph Explorer", use_container_width=True)

        st.markdown("---")

        # Quick insights
        st.markdown("### 💡 Quick Insights")
        results = st.session_state.analysis_results
        graph_summary = st.session_state.get('graph_summary', {})
        enrichment_summary = st.session_state.get('enrichment_summary', {})

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{st.session_state.health_score}</div>
                <div class="stat-label">Health Score</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{graph_summary.get('files_analyzed', 0)}</div>
                <div class="stat-label">Files Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{results.get('complexity', {}).get('hotspot_count', 0)}</div>
                <div class="stat-label">Hotspots</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{enrichment_summary.get('modules_enriched', 0)}</div>
                <div class="stat-label">Modules</div>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    render_sidebar()
    render_main_area()


if __name__ == "__main__":
    main()

# Made with Bob
