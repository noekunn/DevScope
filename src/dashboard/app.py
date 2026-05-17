"""
DevScope - Intelligent Codebase Onboarding Dashboard

Main Streamlit application with premium dark theme and full pipeline orchestration.
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

# Custom CSS for premium dark theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --bg-primary: #0a0f1c;
        --bg-secondary: #111827;
        --bg-tertiary: #1f2937;
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --text-primary: #f9fafb;
        --text-secondary: #d1d5db;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Background gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0f1c 0%, #111827 50%, #1a1f35 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0a0f1c 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Logo glow effect */
    .logo-container {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 1rem;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }
    
    .logo-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(99, 102, 241, 0.5);
        margin: 0;
        padding: 0;
    }
    
    .logo-subtitle {
        color: #d1d5db;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: #1f2937;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 0.5rem;
        color: #f9fafb;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Health score gauge */
    .health-gauge {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 1rem;
        margin: 1rem 0;
    }
    
    .health-score {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #6366f1 50%, #ef4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Navigation cards */
    .nav-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.6);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s ease-in-out infinite;
    }
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
            # Treat as local path
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
        # Generate guides for all roles
        guides = {
            'fullstack': onboarding_gen.generate_guide('fullstack'),
            'frontend': onboarding_gen.generate_guide('frontend'),
            'backend': onboarding_gen.generate_guide('backend'),
            'devops': onboarding_gen.generate_guide('devops')
        }
        time.sleep(0.5)
        progress_bar.progress(100)
        
        # Store results with consistent keys
        # Build per-file data with language info for X-Ray page
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
        # Cleanup temp directory on failure
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        return False


def render_sidebar():
    """Render the sidebar with logo and controls."""
    with st.sidebar:
        # Logo with glow effect
        st.markdown("""
        <div class="logo-container">
            <h1 class="logo-title">🔍 DevScope</h1>
            <p class="logo-subtitle">Intelligent Codebase Onboarding</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Repository input
        st.markdown("### 📂 Repository")
        repo_input = st.text_input(
            "Enter repository path or GitHub URL",
            placeholder="/path/to/repo or https://github.com/user/repo",
            help="Provide a local path or GitHub repository URL"
        )
        
        # Analyze button
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
        
        # Health Score Gauge
        if st.session_state.analyzed:
            st.markdown("### 💚 Codebase Health")
            score = st.session_state.health_score
            
            # Determine color based on score
            if score >= 75:
                color = "#10b981"
                rating = "Excellent"
            elif score >= 50:
                color = "#f59e0b"
                rating = "Good"
            else:
                color = "#ef4444"
                rating = "Needs Attention"
            
            st.markdown(f"""
            <div class="health-gauge">
                <div class="health-score" style="color: {color};">{score}</div>
                <p style="color: #d1d5db; font-size: 1.2rem; margin-top: 0.5rem;">{rating}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick stats
            results = st.session_state.analysis_results
            graph_summary = st.session_state.get('graph_summary', {})
            enrichment_summary = st.session_state.get('enrichment_summary', {})
            if results:
                st.markdown("### 📊 Quick Stats")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Files", graph_summary.get('files_analyzed', 0))
                    st.metric("Modules", enrichment_summary.get('modules_enriched', 0))
                with col2:
                    st.metric("Functions", results.get('complexity', {}).get('total_functions', 0))
                    st.metric("Hotspots", results.get('complexity', {}).get('hotspot_count', 0))
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        DevScope uses AI and graph analysis to help developers understand codebases faster.
        
        **Features:**
        - 🔍 Dependency analysis
        - 📊 Complexity metrics
        - 🕸️ Knowledge graphs
        - 🤖 AI-powered insights
        - 📚 Role-based onboarding
        """)


def render_main_area():
    """Render the main content area."""
    if not st.session_state.analyzed:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h1 style="font-size: 3.5rem; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Welcome to DevScope
            </h1>
            <p style="font-size: 1.3rem; color: #d1d5db; margin-top: 1rem;">
                Intelligent codebase onboarding powered by AI and graph analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #6366f1;">🔍 Deep Analysis</h3>
                <p style="color: #d1d5db;">
                    Analyze dependencies, complexity, and architecture patterns automatically
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #8b5cf6;">🤖 AI-Powered</h3>
                <p style="color: #d1d5db;">
                    IBM Granite LLM provides intelligent insights and explanations
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #10b981;">📚 Smart Onboarding</h3>
                <p style="color: #d1d5db;">
                    Role-specific guides help developers get productive faster
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Getting started
        st.markdown("## 🚀 Getting Started")
        st.markdown("""
        1. **Enter your repository path** in the sidebar
        2. **Click 'Analyze Codebase'** to start the analysis
        3. **Explore the results** across four interactive dashboards
        4. **Generate onboarding guides** for your team
        
        The analysis takes 2-5 minutes depending on codebase size.
        """)
        
    else:
        # Navigation to dashboard pages
        st.markdown("## 📊 Explore Your Codebase")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="nav-card">
                <h3>🔬 Codebase X-Ray</h3>
                <p style="color: #d1d5db;">
                    Visualize dependencies, complexity hotspots, and architecture
                </p>
                <p style="color: #6366f1; margin-top: 1rem;">→ Go to page</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="nav-card">
                <h3>🔄 Modernization</h3>
                <p style="color: #d1d5db;">
                    AI-detected refactoring opportunities and technical debt
                </p>
                <p style="color: #6366f1; margin-top: 1rem;">→ Go to page</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="nav-card">
                <h3>📚 Onboarding Hub</h3>
                <p style="color: #d1d5db;">
                    Role-specific guides and learning paths for new developers
                </p>
                <p style="color: #6366f1; margin-top: 1rem;">→ Go to page</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="nav-card">
                <h3>🕸️ Graph Explorer</h3>
                <p style="color: #d1d5db;">
                    Interactive knowledge graph with PageRank and communities
                </p>
                <p style="color: #6366f1; margin-top: 1rem;">→ Go to page</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick insights
        st.markdown("## 💡 Quick Insights")
        results = st.session_state.analysis_results
        graph_summary = st.session_state.get('graph_summary', {})
        enrichment_summary = st.session_state.get('enrichment_summary', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Health Score",
                f"{st.session_state.health_score}/100",
                delta=None
            )
        with col2:
            st.metric(
                "Total Files",
                graph_summary.get('files_analyzed', 0)
            )
        with col3:
            st.metric(
                "Complexity Hotspots",
                results.get('complexity', {}).get('hotspot_count', 0)
            )
        with col4:
            st.metric(
                "Modules Detected",
                enrichment_summary.get('modules_enriched', 0)
            )


def main():
    """Main application entry point."""
    render_sidebar()
    render_main_area()


if __name__ == "__main__":
    main()

# Made with Bob
