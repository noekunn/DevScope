"""
Onboarding Hub - Role-Specific Onboarding Guide Page.
"""

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from typing import Optional

st.set_page_config(page_title="Onboarding Hub - DevScope", page_icon="📚", layout="wide")

from src.dashboard.components.theme import inject_theme, render_shared_sidebar
inject_theme()
render_shared_sidebar()

st.markdown("""
<style>
    .guide-container { background: #ffffff; border: 1px solid #e8e5df; border-radius: 20px; padding: 2rem; margin-top: 1rem; }
    .guide-title { font-size: 1.5rem; font-weight: 700; color: #1c1917; margin-bottom: 1rem; }
    .guide-container h2 { border-left: 4px solid #ec4899; padding-left: 1rem; }
    .guide-container code { background: #fdf2f8; color: #ec4899; padding: 0.2rem 0.4rem; border-radius: 4px; }
    .guide-container pre { background: #fafaf9; border: 1px solid #e8e5df; border-radius: 8px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

ROLES = {
    'frontend': {'icon': '🖥️', 'title': 'Frontend', 'description': 'UI components, state management, routing, and styling patterns'},
    'backend': {'icon': '⚙️', 'title': 'Backend', 'description': 'APIs, database schemas, business logic, and service architecture'},
    'fullstack': {'icon': '🔄', 'title': 'Fullstack', 'description': 'Complete system overview covering frontend, backend, and integration'},
    'devops': {'icon': '🛠️', 'title': 'DevOps', 'description': 'Deployment, CI/CD, infrastructure, monitoring, and operations'}
}


def render_role_selector(selected_role: Optional[str] = None):
    st.markdown('<div class="subtitle">Select your role to generate a personalized onboarding guide</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, (role_key, role_info) in enumerate(ROLES.items()):
        with cols[idx]:
            if st.button(
                f"{role_info['icon']}\n\n{role_info['title']}\n\n{role_info['description']}",
                key=f"role_{role_key}", use_container_width=True,
                type="primary" if role_key == selected_role else "secondary"
            ):
                st.session_state['selected_role'] = role_key
                st.rerun()


def generate_guide(role: str, repo_path: str) -> str:
    cache_key = f'guide_{role}'
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    pre_generated = st.session_state.get('guides', {})
    if role in pre_generated:
        st.session_state[cache_key] = pre_generated[role]
        return pre_generated[role]
    try:
        from src.generators import OnboardingGenerator
        with st.spinner(f'🔮 Generating {ROLES[role]["title"]} onboarding guide...'):
            generator = OnboardingGenerator(repo_path)
            guide = generator.generate_guide(role)
            st.session_state[cache_key] = guide
        return guide
    except Exception as e:
        return f"# Onboarding Guide ({role.title()})\n\n*Error: {e}*"


def render_guide(role: str, guide: str):
    role_info = ROLES[role]
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="guide-title">{role_info["icon"]} {role_info["title"]} Onboarding Guide</div>', unsafe_allow_html=True)
    with col2:
        st.download_button("📥 Download Guide", data=guide, file_name=f"onboarding_{role}.md", mime="text/markdown", use_container_width=True)
    st.markdown("---")
    st.markdown(guide, unsafe_allow_html=True)


def main():
    st.markdown('<div class="gradient-header">📚 Onboarding Hub</div>', unsafe_allow_html=True)

    if not st.session_state.get('analysis_complete', False):
        st.markdown("""
        <div class="info-message">
            <div class="info-icon">🔍</div>
            <div class="info-text">No analysis data available</div>
            <p style="color: #78716c;">Please run the analysis from the Home page first.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    repo_path = st.session_state.get('repo_path', '')
    if 'selected_role' not in st.session_state:
        st.session_state['selected_role'] = None

    render_role_selector(st.session_state['selected_role'])

    if st.session_state['selected_role']:
        role = st.session_state['selected_role']
        try:
            guide = generate_guide(role, repo_path)
            st.markdown('<div class="guide-container">', unsafe_allow_html=True)
            render_guide(role, guide)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error generating guide: {e}")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #78716c;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">👆</div>
            <div style="font-size: 1.2rem;">Select a role above to generate your personalized onboarding guide</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# Made with Bob
