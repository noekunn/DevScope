"""
Health Score Component — Codebase health gauge for dashboard.
"""
import streamlit as st


def render_health_gauge(score: int, size: str = "large") -> None:
    """
    Render a health score gauge.
    
    Args:
        score: Health score from 0-100.
        size: 'large' for main page, 'small' for sidebar.
    """
    if score >= 80:
        color, rating = '#10b981', 'Excellent'
    elif score >= 60:
        color, rating = '#3b82f6', 'Good'
    elif score >= 40:
        color, rating = '#f59e0b', 'Fair'
    else:
        color, rating = '#ef4444', 'Needs Improvement'
    
    font_size = '4rem' if size == 'large' else '2rem'
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem;
         background: linear-gradient(135deg, #1e293b, #334155);
         border-radius: 16px; border: 1px solid #475569;">
        <div style="color: #94a3b8; text-transform: uppercase; 
             letter-spacing: 0.1em; font-size: 0.9rem;">Health Score</div>
        <div style="font-size: {font_size}; font-weight: 900; color: {color};
             margin: 0.5rem 0;">{score}/100</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #e2e8f0;">{rating}</div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value, color: str = "#6366f1") -> None:
    """Render a single metric card."""
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem;
         background: linear-gradient(135deg, #1e293b, #334155);
         border-radius: 12px; border: 1px solid #475569;">
        <div style="font-size: 2.5rem; font-weight: 800; color: {color};">{value}</div>
        <div style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# Made with Bob
