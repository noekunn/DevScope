"""
Onboarding Hub - Role-Specific Onboarding Guide Page.

Provides role-specific onboarding guides for:
- Frontend developers
- Backend developers
- Fullstack developers
- DevOps engineers
"""

import sys
from pathlib import Path

# Add project root to path for absolute imports
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from typing import Dict, Optional

# Page configuration
st.set_page_config(
    page_title="Onboarding Hub - DevScope",
    page_icon="📚",
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
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Role cards */
    .role-cards-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .role-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 2rem;
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .role-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 16px;
        padding: 2px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .role-card:hover::before {
        opacity: 1;
    }
    
    .role-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(99, 102, 241, 0.4);
    }
    
    .role-card.selected {
        border: 2px solid #6366f1;
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.5);
    }
    
    .role-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .role-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.75rem;
    }
    
    .role-description {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Guide container */
    .guide-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #475569;
        margin-top: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .guide-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #475569;
    }
    
    .guide-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Markdown styling */
    .guide-container h1 {
        color: #e2e8f0;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .guide-container h2 {
        color: #cbd5e1;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #6366f1;
        padding-left: 1rem;
    }
    
    .guide-container h3 {
        color: #cbd5e1;
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .guide-container p {
        color: #94a3b8;
        line-height: 1.8;
        margin-bottom: 1rem;
    }
    
    .guide-container ul, .guide-container ol {
        color: #94a3b8;
        line-height: 1.8;
        margin-bottom: 1rem;
        padding-left: 2rem;
    }
    
    .guide-container li {
        margin-bottom: 0.5rem;
    }
    
    .guide-container code {
        background: #0f172a;
        color: #8b5cf6;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }
    
    .guide-container pre {
        background: #0f172a;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
        margin-bottom: 1rem;
    }
    
    .guide-container pre code {
        background: transparent;
        color: #e2e8f0;
        padding: 0;
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
    
    /* Loading spinner */
    .loading-container {
        text-align: center;
        padding: 3rem;
    }
    
    .loading-text {
        color: #cbd5e1;
        font-size: 1.2rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Role definitions
ROLES = {
    'frontend': {
        'icon': '🖥️',
        'title': 'Frontend',
        'description': 'UI components, state management, routing, and styling patterns'
    },
    'backend': {
        'icon': '⚙️',
        'title': 'Backend',
        'description': 'APIs, database schemas, business logic, and service architecture'
    },
    'fullstack': {
        'icon': '🔄',
        'title': 'Fullstack',
        'description': 'Complete system overview covering frontend, backend, and integration'
    },
    'devops': {
        'icon': '🛠️',
        'title': 'DevOps',
        'description': 'Deployment, CI/CD, infrastructure, monitoring, and operations'
    }
}


def render_role_selector(selected_role: Optional[str] = None):
    """Render role selection cards."""
    st.markdown('<div class="subtitle">Select your role to generate a personalized onboarding guide</div>', unsafe_allow_html=True)
    
    # Create 4 columns for role cards
    cols = st.columns(4)
    
    for idx, (role_key, role_info) in enumerate(ROLES.items()):
        with cols[idx]:
            selected_class = 'selected' if role_key == selected_role else ''
            
            # Create clickable card using button
            if st.button(
                f"{role_info['icon']}\n\n{role_info['title']}\n\n{role_info['description']}",
                key=f"role_{role_key}",
                use_container_width=True,
                type="primary" if role_key == selected_role else "secondary"
            ):
                st.session_state['selected_role'] = role_key
                st.rerun()


def generate_guide(role: str, repo_path: str) -> str:
    """Generate onboarding guide for the specified role."""
    # Check if guide is already cached
    cache_key = f'guide_{role}'
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Check if guides were pre-generated during analysis
    pre_generated = st.session_state.get('guides', {})
    if role in pre_generated:
        st.session_state[cache_key] = pre_generated[role]
        return pre_generated[role]
    
    # Generate new guide
    try:
        from src.generators import OnboardingGenerator
        with st.spinner(f'🔮 Generating {ROLES[role]["title"]} onboarding guide...'):
            generator = OnboardingGenerator(repo_path)
            guide = generator.generate_guide(role)
            st.session_state[cache_key] = guide
        return guide
    except Exception as e:
        return f"# Onboarding Guide ({role.title()})\n\n*Guide generation encountered an error: {e}*\n\nPlease ensure all dependencies are installed and try again."


def render_guide(role: str, guide: str):
    """Render the generated guide with download button."""
    role_info = ROLES[role]
    
    # Guide header with download button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<div class="guide-title">{role_info["icon"]} {role_info["title"]} Onboarding Guide</div>', unsafe_allow_html=True)
    
    with col2:
        # Download button
        st.download_button(
            label="📥 Download Guide",
            data=guide,
            file_name=f"onboarding_{role}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Render the guide content
    st.markdown(guide, unsafe_allow_html=True)


def main():
    """Main Onboarding Hub page."""
    st.markdown('<div class="gradient-header">📚 Onboarding Hub</div>', unsafe_allow_html=True)
    
    # Debug: Show session state keys
    # st.write("Session state keys:", list(st.session_state.keys()))
    
    # Check if analysis has been run
    if not st.session_state.get('analysis_complete', False):
        st.markdown("""
        <div class="info-message">
            <div class="info-icon">🔍</div>
            <div class="info-text">No analysis data available</div>
            <p style="color: #94a3b8;">Please run the analysis from the Home page first to generate onboarding guides.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    repo_path = st.session_state.get('repo_path', '')
    
    # Initialize selected role in session state
    if 'selected_role' not in st.session_state:
        st.session_state['selected_role'] = None
    
    # Render role selector
    render_role_selector(st.session_state['selected_role'])
    
    # If a role is selected, generate and display guide
    if st.session_state['selected_role']:
        role = st.session_state['selected_role']
        
        try:
            # Generate guide (uses cache if available)
            guide = generate_guide(role, repo_path)
            
            # Render guide in container
            st.markdown('<div class="guide-container">', unsafe_allow_html=True)
            render_guide(role, guide)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error generating guide: {e}")
            st.info("Please ensure the analysis has completed successfully and try again.")
    else:
        # Show helpful message when no role selected
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #94a3b8;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">👆</div>
            <div style="font-size: 1.2rem;">Select a role above to generate your personalized onboarding guide</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# Made with Bob
