"""
Shared warm theme CSS and sidebar navigation for all DevScope pages.
Inspired by weco.ai — cream background, pink-orange accents, white cards.
"""

WARM_THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp {
        background-color: #f5f4ef !important;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e8e5df;
    }
    [data-testid="stSidebar"] * { color: #1c1917 !important; }

    /* Hide ugly default page nav on ALL pages */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Style page_link buttons in sidebar */
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

    .stMarkdown, .stMarkdown p, .stMarkdown li, label { color: #1c1917 !important; }
    h1, h2, h3, h4, h5, h6 {
        color: #1c1917 !important;
        font-family: 'Inter', sans-serif !important;
        -webkit-text-fill-color: #1c1917 !important;
        background: none !important;
        -webkit-background-clip: unset !important;
    }

    .gradient-header {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.5rem;
    }
    .subtitle { color: #78716c !important; font-size: 1.1rem; margin-bottom: 2rem; }

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
    }
    .wcard h3 { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; }
    .wcard p { color: #78716c !important; line-height: 1.6; }

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
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e8e5df;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); }
    .metric-value { font-size: 2.5rem; font-weight: 800; }
    .metric-value.critical { color: #dc2626; }
    .metric-value.high { color: #ea580c; }
    .metric-value.medium { color: #2563eb; }
    .metric-label { color: #78716c; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

    .health-card {
        background: linear-gradient(135deg, #fdf2f8, #fff7ed);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid #fce7f3;
        text-align: center;
        margin-bottom: 2rem;
    }
    .health-score { font-size: 4rem; font-weight: 900; margin: 1rem 0; }
    .health-score.excellent { color: #16a34a; }
    .health-score.good { color: #2563eb; }
    .health-score.fair { color: #ea580c; }
    .health-score.poor { color: #dc2626; }
    .health-label { color: #78716c; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.1em; }
    .health-rating { font-size: 1.5rem; font-weight: 600; color: #1c1917; margin-top: 0.5rem; }

    .section-header {
        font-size: 1.5rem; font-weight: 700; color: #1c1917;
        margin-top: 2rem; margin-bottom: 1rem;
        padding-bottom: 0.5rem; border-bottom: 2px solid #e8e5df;
    }

    .issue-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        border-left: 4px solid;
        margin-bottom: 1rem;
        border: 1px solid #e8e5df;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .issue-card.critical { border-left: 4px solid #dc2626; }
    .issue-card.high { border-left: 4px solid #ea580c; }
    .issue-card.medium { border-left: 4px solid #2563eb; }
    .issue-title { font-size: 1.1rem; font-weight: 700; color: #1c1917; margin-bottom: 0.5rem; }
    .issue-description { color: #57534e; font-size: 0.95rem; line-height: 1.6; }
    .issue-meta { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e8e5df; }
    .issue-meta-item { color: #78716c; font-size: 0.85rem; }
    .issue-meta-label { font-weight: 600; color: #1c1917; }
    .issue-files { background: #fafaf9; border-radius: 8px; padding: 0.75rem; margin-top: 0.5rem; font-family: monospace; font-size: 0.85rem; color: #9333ea; }

    .info-message {
        background: #ffffff;
        border-left: 4px solid #ec4899;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #e8e5df;
    }
    .info-icon { font-size: 3rem; margin-bottom: 1rem; }
    .info-text { color: #1c1917; font-size: 1.2rem; margin-bottom: 1rem; }

    .role-card {
        background: #ffffff;
        border: 1px solid #e8e5df;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .role-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        border-color: #ec4899;
    }
    .role-icon { font-size: 2rem; margin-bottom: 0.75rem; }
    .role-name { font-size: 1.1rem; font-weight: 700; color: #1c1917; margin-bottom: 0.5rem; }
    .role-desc { color: #78716c; font-size: 0.85rem; line-height: 1.5; }

    .stButton > button {
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 12px rgba(236,72,153,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(236,72,153,0.4) !important;
    }

    [data-testid="stMetric"] { background: #ffffff; border: 1px solid #e8e5df; border-radius: 12px; padding: 0.75rem; }
    [data-testid="stMetricValue"] { color: #1c1917 !important; }
    [data-testid="stMetricLabel"] { color: #78716c !important; }

    hr { border-color: #e8e5df !important; }
</style>
"""


def inject_theme():
    """Inject the warm theme CSS into a Streamlit page."""
    import streamlit as st
    st.markdown(WARM_THEME_CSS, unsafe_allow_html=True)


def render_shared_sidebar():
    """Render the shared sidebar navigation on sub-pages."""
    import streamlit as st

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 1rem;margin-bottom:1rem;background:linear-gradient(135deg,#fdf2f8,#fff7ed);border-radius:16px;border:1px solid #fce7f3;">
            <div style="font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#ec4899,#f97316);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔍 DevScope</div>
            <div style="color:#78716c !important;font-size:0.85rem;margin-top:0.25rem;">Intelligent Codebase Onboarding</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Navigation")
        st.page_link("app.py", label="🏠  Home", use_container_width=True)
        st.page_link("pages/01_codebase_xray.py", label="🔬  Codebase X-Ray", use_container_width=True)
        st.page_link("pages/02_onboarding_hub.py", label="📚  Onboarding Hub", use_container_width=True)
        st.page_link("pages/03_modernization.py", label="🔄  Modernization", use_container_width=True)
        st.page_link("pages/04_graph_explorer.py", label="🕸️  Graph Explorer", use_container_width=True)

        st.markdown("---")
