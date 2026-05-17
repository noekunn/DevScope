"""
Modernization Roadmap - Technical Debt and Improvement Planning Page.

Provides a prioritized roadmap for codebase modernization:
- Health score summary
- Issue categorization by priority
- Detailed recommendations with effort estimates
- Downloadable roadmap
"""

import sys
from pathlib import Path

# Add project root to path for absolute imports
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="Modernization - DevScope",
    page_icon="🔄",
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
    
    /* Health score card */
    .health-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #475569;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    
    .health-score {
        font-size: 4rem;
        font-weight: 900;
        margin: 1rem 0;
    }
    
    .health-score.excellent { color: #10b981; }
    .health-score.good { color: #3b82f6; }
    .health-score.fair { color: #f59e0b; }
    .health-score.poor { color: #ef4444; }
    
    .health-label {
        color: #94a3b8;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    
    .health-rating {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-top: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #475569;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .metric-value.critical { color: #ef4444; }
    .metric-value.high { color: #f59e0b; }
    .metric-value.medium { color: #3b82f6; }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Priority badges */
    .priority-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .priority-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .priority-high {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .priority-medium {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #475569;
    }
    
    /* Issue cards */
    .issue-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .issue-card.critical { border-left-color: #ef4444; }
    .issue-card.high { border-left-color: #f59e0b; }
    .issue-card.medium { border-left-color: #3b82f6; }
    
    .issue-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    .issue-description {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .issue-meta {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #475569;
    }
    
    .issue-meta-item {
        color: #94a3b8;
        font-size: 0.85rem;
    }
    
    .issue-meta-label {
        font-weight: 600;
        color: #cbd5e1;
    }
    
    .issue-files {
        background: #0f172a;
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #8b5cf6;
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
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)


def parse_roadmap_issues(roadmap_text: str) -> Dict[str, List[Dict[str, Any]]]:
    """Parse the roadmap markdown to extract issues by priority."""
    issues = {
        'critical': [],
        'high': [],
        'medium': []
    }
    
    lines = roadmap_text.split('\n')
    current_priority = None
    current_issue = None
    
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Detect priority sections (handles ## and ### headers, with/without emoji)
        if 'critical' in line_lower and ('priority' in line_lower or 'issue' in line_lower):
            current_priority = 'critical'
            current_issue = None
        elif 'high' in line_lower and 'priority' in line_lower:
            current_priority = 'high'
            current_issue = None
        elif 'medium' in line_lower and 'priority' in line_lower:
            current_priority = 'medium'
            current_issue = None
        elif 'implementation strategy' in line_lower or 'success metrics' in line_lower:
            current_priority = None
            current_issue = None
        
        # Detect issue items (### numbered headers like "### 1. High Complexity: file.py")
        elif current_priority and line_stripped.startswith('###') and any(c.isdigit() for c in line_stripped[:8]):
            issue_text = line_stripped.lstrip('#').strip()
            # Remove leading number + dot
            for i, c in enumerate(issue_text):
                if c == '.' and i > 0:
                    issue_text = issue_text[i+1:].strip()
                    break
            
            if issue_text and len(issue_text) > 5:
                current_issue = {
                    'description': issue_text,
                    'files': [],
                    'effort': 'Unknown',
                    'suggestion': ''
                }
                issues[current_priority].append(current_issue)
        
        # Detect numbered items (e.g., "1. something")
        elif current_priority and line_stripped and len(line_stripped) > 10:
            if line_stripped[0].isdigit() and '.' in line_stripped[:4]:
                issue_text = line_stripped.split('.', 1)[1].strip()
                if issue_text and len(issue_text) > 10:
                    current_issue = {
                        'description': issue_text,
                        'files': [],
                        'effort': 'Unknown',
                        'suggestion': ''
                    }
                    issues[current_priority].append(current_issue)
        
        # Extract metadata from current issue
        if current_issue:
            if ('/' in line_stripped or '\\' in line_stripped) and any(ext in line_stripped for ext in ['.py', '.js', '.ts', '.java', '.go']):
                current_issue['files'].append(line_stripped.lstrip('- '))
            elif 'effort' in line_lower:
                current_issue['effort'] = line_stripped.split(':')[-1].strip().strip('*')
            elif 'suggestion' in line_lower or 'approach' in line_lower:
                current_issue['suggestion'] = line_stripped.split(':')[-1].strip().strip('*')
    
    # If parsing failed, fall back to data-driven approach
    total_parsed = sum(len(v) for v in issues.values())
    if total_parsed == 0:
        issues = _build_issues_from_session()
    
    return issues


def _build_issues_from_session() -> Dict[str, List[Dict[str, Any]]]:
    """Build issues directly from analysis data in session state."""
    issues = {'critical': [], 'high': [], 'medium': []}
    
    results = st.session_state.get('analysis_results', {})
    complexity = results.get('complexity', {})
    files = complexity.get('files', [])
    
    for f in files:
        max_c = f.get('max_complexity', 0)
        if max_c > 20:
            issues['critical'].append({
                'description': f"High Complexity: {f['path']} (complexity {max_c})",
                'files': [f['path']],
                'effort': 'Large',
                'suggestion': 'Break down complex functions into smaller units'
            })
        elif max_c > 10:
            issues['high'].append({
                'description': f"Moderate Complexity: {f['path']} (complexity {max_c})",
                'files': [f['path']],
                'effort': 'Medium',
                'suggestion': 'Refactor conditional logic and extract helper methods'
            })
        elif max_c > 5:
            issues['medium'].append({
                'description': f"Minor Complexity: {f['path']} (complexity {max_c})",
                'files': [f['path']],
                'effort': 'Small',
                'suggestion': 'Add documentation and simplify where possible'
            })
    
    return issues


def render_health_summary(health_score: int):
    """Render health score summary."""
    # Determine rating and color
    if health_score >= 80:
        rating = "Excellent"
        color_class = "excellent"
    elif health_score >= 60:
        rating = "Good"
        color_class = "good"
    elif health_score >= 40:
        rating = "Fair"
        color_class = "fair"
    else:
        rating = "Needs Improvement"
        color_class = "poor"
    
    st.markdown(f"""
    <div class="health-card">
        <div class="health-label">Codebase Health Score</div>
        <div class="health-score {color_class}">{health_score}/100</div>
        <div class="health-rating">{rating}</div>
    </div>
    """, unsafe_allow_html=True)


def render_issue_overview(issues: Dict[str, List[Dict[str, Any]]]):
    """Render issue count overview."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔴 Critical Issues</div>
            <div class="metric-value critical">{len(issues['critical'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🟠 High Priority</div>
            <div class="metric-value high">{len(issues['high'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🟡 Medium Priority</div>
            <div class="metric-value medium">{len(issues['medium'])}</div>
        </div>
        """, unsafe_allow_html=True)


def render_priority_section(priority: str, issues: List[Dict[str, Any]], icon: str, color: str):
    """Render a priority section with expandable issues."""
    if not issues:
        return
    
    st.markdown(f'<div class="section-header">{icon} {priority.title()} Priority ({len(issues)} issues)</div>', unsafe_allow_html=True)
    
    for idx, issue in enumerate(issues, 1):
        with st.expander(f"**Issue {idx}:** {issue['description'][:80]}{'...' if len(issue['description']) > 80 else ''}"):
            st.markdown(f"""
            <div class="issue-card {priority}">
                <div class="issue-title">{issue['description']}</div>
                
                {f'<div class="issue-description"><strong>Suggestion:</strong> {issue["suggestion"]}</div>' if issue['suggestion'] else ''}
                
                <div class="issue-meta">
                    <div class="issue-meta-item">
                        <span class="issue-meta-label">Effort:</span> {issue['effort']}
                    </div>
                    <div class="issue-meta-item">
                        <span class="issue-meta-label">Affected Files:</span> {len(issue['files'])}
                    </div>
                </div>
                
                {f'<div class="issue-files">{chr(10).join(issue["files"][:5])}</div>' if issue['files'] else ''}
            </div>
            """, unsafe_allow_html=True)


def generate_roadmap(repo_path: str) -> str:
    """Generate modernization roadmap."""
    # Check if roadmap is already cached
    if 'modernization_roadmap' in st.session_state:
        return st.session_state['modernization_roadmap']
    
    # Try to generate with AI planner
    try:
        from src.generators import ModernizationPlanner
        with st.spinner('🔮 Analyzing codebase and generating modernization roadmap...'):
            planner = ModernizationPlanner(repo_path)
            roadmap = planner.generate_roadmap()
            st.session_state['modernization_roadmap'] = roadmap
        return roadmap
    except Exception as e:
        # Fallback: Generate roadmap from analysis data
        roadmap = _generate_fallback_roadmap()
        st.session_state['modernization_roadmap'] = roadmap
        return roadmap


def _generate_fallback_roadmap() -> str:
    """Generate a roadmap from the complexity analysis data stored in session state."""
    results = st.session_state.get('analysis_results', {})
    complexity = results.get('complexity', {})
    files = complexity.get('files', [])
    health_score = complexity.get('health_score', 0)
    
    roadmap = "# Modernization Roadmap\n\n"
    roadmap += "*Generated by DevScope - Intelligent Codebase Analysis*\n\n---\n\n"
    
    # Health summary
    roadmap += f"## 📊 Health Score Breakdown\n\n"
    roadmap += f"**Overall Health**: {health_score}/100\n\n"
    roadmap += f"**Files Analyzed**: {complexity.get('total_files', 0)}\n"
    roadmap += f"**Total Functions**: {complexity.get('total_functions', 0)}\n"
    roadmap += f"**Average Complexity**: {complexity.get('avg_complexity', 0)}\n\n"
    
    # Find hotspots
    hotspot_files = [f for f in files if f.get('hotspot_count', 0) > 0]
    complex_files = sorted(files, key=lambda x: x.get('max_complexity', 0), reverse=True)
    
    # Critical Priority
    roadmap += "## 🔴 Critical Priority\n\n"
    critical_items = [f for f in complex_files if f.get('max_complexity', 0) > 20]
    if critical_items:
        roadmap += f"**{len(critical_items)} issue(s) identified**\n\n"
        for i, f in enumerate(critical_items[:5], 1):
            roadmap += f"### {i}. High Complexity: {f['path']}\n\n"
            roadmap += f"- Max complexity: {f.get('max_complexity', 0)}\n"
            roadmap += f"- Lines: {f.get('total_lines', 0)}\n"
            roadmap += f"- Hotspots: {f.get('hotspot_count', 0)} functions\n"
            roadmap += f"- **Suggestion**: Break down complex functions into smaller units\n\n"
    else:
        roadmap += "*No critical priority issues found. Great job!*\n\n"
    
    # High Priority
    roadmap += "---\n\n## 🟠 High Priority\n\n"
    high_items = [f for f in complex_files if 10 < f.get('max_complexity', 0) <= 20]
    if high_items:
        roadmap += f"**{len(high_items)} issue(s) identified**\n\n"
        for i, f in enumerate(high_items[:5], 1):
            roadmap += f"### {i}. Moderate Complexity: {f['path']}\n\n"
            roadmap += f"- Max complexity: {f.get('max_complexity', 0)}\n"
            roadmap += f"- Functions: {f.get('function_count', 0)}\n"
            roadmap += f"- **Effort**: Medium\n"
            roadmap += f"- **Suggestion**: Refactor conditional logic and extract helper methods\n\n"
    else:
        roadmap += "*No high priority issues found.*\n\n"
    
    # Medium Priority
    roadmap += "---\n\n## 🟡 Medium Priority\n\n"
    medium_items = [f for f in complex_files if 5 < f.get('max_complexity', 0) <= 10]
    if medium_items:
        roadmap += f"**{len(medium_items)} issue(s) identified**\n\n"
        for i, f in enumerate(medium_items[:5], 1):
            roadmap += f"### {i}. Code Improvement: {f['path']}\n\n"
            roadmap += f"- Complexity: {f.get('max_complexity', 0)}\n"
            roadmap += f"- **Effort**: Small\n"
            roadmap += f"- **Suggestion**: Add documentation and simplify where possible\n\n"
    else:
        roadmap += "*No medium priority issues found.*\n\n"
    
    roadmap += "---\n\n## 🎯 Implementation Strategy\n\n"
    roadmap += "1. **Address Critical Issues First** - Refactor high-complexity hotspots\n"
    roadmap += "2. **Tackle High Priority Items** - Reduce moderate complexity\n"
    roadmap += "3. **Continuous Improvement** - Monitor metrics and prevent new debt\n"
    
    return roadmap


def main():
    """Main Modernization Roadmap page."""
    st.markdown('<div class="gradient-header">🔄 Modernization Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Prioritized technical debt and improvement recommendations</div>', unsafe_allow_html=True)
    
    # Debug: Show session state keys
    # st.write("Session state keys:", list(st.session_state.keys()))
    
    # Check if analysis has been run
    if not st.session_state.get('analysis_complete', False):
        st.markdown("""
        <div class="info-message">
            <div class="info-icon">🔍</div>
            <div class="info-text">No analysis data available</div>
            <p style="color: #94a3b8;">Please run the analysis from the Home page first to generate the modernization roadmap.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    repo_path = st.session_state.get('repo_path', '')
    health_score = st.session_state.get('analysis_results', {}).get('health_score', 0)
    
    # Render health summary
    render_health_summary(health_score)
    
    # Generate roadmap button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Generate Roadmap", use_container_width=True, type="primary"):
            # Clear cache to regenerate
            if 'modernization_roadmap' in st.session_state:
                del st.session_state['modernization_roadmap']
    
    # Check if roadmap exists or needs generation
    if 'modernization_roadmap' not in st.session_state:
        # Auto-generate on first visit
        try:
            roadmap = generate_roadmap(repo_path)
        except Exception as e:
            st.error(f"Error generating roadmap: {e}")
            return
    else:
        roadmap = st.session_state['modernization_roadmap']
    
    # Parse issues from roadmap
    issues = parse_roadmap_issues(roadmap)
    
    # Render issue overview
    st.markdown("---")
    render_issue_overview(issues)
    
    # Download button
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.download_button(
            label="📥 Download Roadmap",
            data=roadmap,
            file_name="modernization_roadmap.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # Render priority sections
    st.markdown("---")
    render_priority_section('critical', issues['critical'], '🔴', 'critical')
    render_priority_section('high', issues['high'], '🟠', 'high')
    render_priority_section('medium', issues['medium'], '🟡', 'medium')
    
    # Show full roadmap in expander
    st.markdown("---")
    with st.expander("📄 View Full Roadmap (Markdown)"):
        st.markdown(roadmap)


if __name__ == "__main__":
    main()

# Made with Bob
