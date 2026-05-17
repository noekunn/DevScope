"""
Modernization Roadmap - Technical Debt and Improvement Planning Page.
"""

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from typing import Dict, List, Any

st.set_page_config(page_title="Modernization - DevScope", page_icon="🔄", layout="wide")

from src.dashboard.components.theme import inject_theme
inject_theme()


def parse_roadmap_issues(roadmap_text: str) -> Dict[str, List[Dict[str, Any]]]:
    """Parse the roadmap markdown to extract issues by priority."""
    issues = {'critical': [], 'high': [], 'medium': []}
    lines = roadmap_text.split('\n')
    current_priority = None
    current_issue = None

    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

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
        elif current_priority and line_stripped.startswith('###') and any(c.isdigit() for c in line_stripped[:8]):
            issue_text = line_stripped.lstrip('#').strip()
            for i, c in enumerate(issue_text):
                if c == '.' and i > 0:
                    issue_text = issue_text[i+1:].strip()
                    break
            if issue_text and len(issue_text) > 5:
                current_issue = {'description': issue_text, 'files': [], 'effort': 'Unknown', 'suggestion': ''}
                issues[current_priority].append(current_issue)
        elif current_priority and line_stripped and len(line_stripped) > 10:
            if line_stripped[0].isdigit() and '.' in line_stripped[:4]:
                issue_text = line_stripped.split('.', 1)[1].strip()
                if issue_text and len(issue_text) > 10:
                    current_issue = {'description': issue_text, 'files': [], 'effort': 'Unknown', 'suggestion': ''}
                    issues[current_priority].append(current_issue)

        if current_issue:
            if ('/' in line_stripped or '\\' in line_stripped) and any(ext in line_stripped for ext in ['.py', '.js', '.ts', '.java', '.go']):
                current_issue['files'].append(line_stripped.lstrip('- '))
            elif 'effort' in line_lower:
                current_issue['effort'] = line_stripped.split(':')[-1].strip().strip('*')
            elif 'suggestion' in line_lower or 'approach' in line_lower:
                current_issue['suggestion'] = line_stripped.split(':')[-1].strip().strip('*')

    total_parsed = sum(len(v) for v in issues.values())
    if total_parsed == 0:
        issues = _build_issues_from_session()
    return issues


def _build_issues_from_session() -> Dict[str, List[Dict[str, Any]]]:
    """Build issues directly from analysis data in session state."""
    issues = {'critical': [], 'high': [], 'medium': []}
    results = st.session_state.get('analysis_results', {})
    files = results.get('complexity', {}).get('files', [])

    for f in files:
        max_c = f.get('max_complexity', 0)
        if max_c > 20:
            issues['critical'].append({
                'description': f"High Complexity: {f['path']} (complexity {max_c})",
                'files': [f['path']], 'effort': 'Large',
                'suggestion': 'Break down complex functions into smaller units'
            })
        elif max_c > 10:
            issues['high'].append({
                'description': f"Moderate Complexity: {f['path']} (complexity {max_c})",
                'files': [f['path']], 'effort': 'Medium',
                'suggestion': 'Refactor conditional logic and extract helper methods'
            })
        elif max_c > 5:
            issues['medium'].append({
                'description': f"Minor Complexity: {f['path']} (complexity {max_c})",
                'files': [f['path']], 'effort': 'Small',
                'suggestion': 'Add documentation and simplify where possible'
            })
    return issues


def render_health_summary(health_score: int):
    if health_score >= 80:
        rating, color_class = "Excellent", "excellent"
    elif health_score >= 60:
        rating, color_class = "Good", "good"
    elif health_score >= 40:
        rating, color_class = "Fair", "fair"
    else:
        rating, color_class = "Needs Improvement", "poor"

    st.markdown(f"""
    <div class="health-card">
        <div class="health-label">Codebase Health Score</div>
        <div class="health-score {color_class}">{health_score}/100</div>
        <div class="health-rating">{rating}</div>
    </div>
    """, unsafe_allow_html=True)


def render_issue_overview(issues: Dict[str, List[Dict[str, Any]]]):
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
                    <div class="issue-meta-item"><span class="issue-meta-label">Effort:</span> {issue['effort']}</div>
                    <div class="issue-meta-item"><span class="issue-meta-label">Affected Files:</span> {len(issue['files'])}</div>
                </div>
                {f'<div class="issue-files">{chr(10).join(issue["files"][:5])}</div>' if issue['files'] else ''}
            </div>
            """, unsafe_allow_html=True)


def generate_roadmap(repo_path: str) -> str:
    if 'modernization_roadmap' in st.session_state:
        return st.session_state['modernization_roadmap']
    try:
        from src.generators import ModernizationPlanner
        with st.spinner('🔮 Generating modernization roadmap...'):
            planner = ModernizationPlanner(repo_path)
            roadmap = planner.generate_roadmap()
            st.session_state['modernization_roadmap'] = roadmap
        return roadmap
    except Exception:
        roadmap = _generate_fallback_roadmap()
        st.session_state['modernization_roadmap'] = roadmap
        return roadmap


def _generate_fallback_roadmap() -> str:
    results = st.session_state.get('analysis_results', {})
    complexity = results.get('complexity', {})
    files = complexity.get('files', [])
    health_score = complexity.get('health_score', 0)

    roadmap = "# Modernization Roadmap\n\n*Generated by DevScope*\n\n---\n\n"
    roadmap += f"## 📊 Health Score Breakdown\n\n**Overall Health**: {health_score}/100\n"
    roadmap += f"**Files Analyzed**: {complexity.get('total_files', 0)}\n"
    roadmap += f"**Total Functions**: {complexity.get('total_functions', 0)}\n"
    roadmap += f"**Average Complexity**: {complexity.get('avg_complexity', 0)}\n\n"

    complex_files = sorted(files, key=lambda x: x.get('max_complexity', 0), reverse=True)

    roadmap += "## 🔴 Critical Priority\n\n"
    critical_items = [f for f in complex_files if f.get('max_complexity', 0) > 20]
    if critical_items:
        for i, f in enumerate(critical_items[:5], 1):
            roadmap += f"### {i}. High Complexity: {f['path']}\n\n"
            roadmap += f"- Max complexity: {f.get('max_complexity', 0)}\n- Lines: {f.get('total_lines', 0)}\n"
            roadmap += f"- **Suggestion**: Break down complex functions\n\n"
    else:
        roadmap += "*No critical priority issues found.*\n\n"

    roadmap += "---\n\n## 🟠 High Priority\n\n"
    high_items = [f for f in complex_files if 10 < f.get('max_complexity', 0) <= 20]
    if high_items:
        for i, f in enumerate(high_items[:5], 1):
            roadmap += f"### {i}. Moderate Complexity: {f['path']}\n\n"
            roadmap += f"- Max complexity: {f.get('max_complexity', 0)}\n- **Effort**: Medium\n\n"
    else:
        roadmap += "*No high priority issues found.*\n\n"

    roadmap += "---\n\n## 🟡 Medium Priority\n\n"
    medium_items = [f for f in complex_files if 5 < f.get('max_complexity', 0) <= 10]
    if medium_items:
        for i, f in enumerate(medium_items[:5], 1):
            roadmap += f"### {i}. Code Improvement: {f['path']}\n\n"
            roadmap += f"- Complexity: {f.get('max_complexity', 0)}\n- **Effort**: Small\n\n"
    else:
        roadmap += "*No medium priority issues found.*\n\n"

    roadmap += "---\n\n## 🎯 Implementation Strategy\n\n"
    roadmap += "1. **Address Critical Issues First**\n2. **Tackle High Priority Items**\n3. **Continuous Improvement**\n"
    return roadmap


def main():
    st.markdown('<div class="gradient-header">🔄 Modernization Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Prioritized technical debt and improvement recommendations</div>', unsafe_allow_html=True)

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
    health_score = st.session_state.get('analysis_results', {}).get('health_score', 0)
    render_health_summary(health_score)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Generate Roadmap", use_container_width=True, type="primary"):
            if 'modernization_roadmap' in st.session_state:
                del st.session_state['modernization_roadmap']

    if 'modernization_roadmap' not in st.session_state:
        try:
            roadmap = generate_roadmap(repo_path)
        except Exception as e:
            st.error(f"Error: {e}")
            return
    else:
        roadmap = st.session_state['modernization_roadmap']

    issues = parse_roadmap_issues(roadmap)

    st.markdown("---")
    render_issue_overview(issues)

    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.download_button("📥 Download Roadmap", data=roadmap, file_name="modernization_roadmap.md", mime="text/markdown", use_container_width=True)

    st.markdown("---")
    render_priority_section('critical', issues['critical'], '🔴', 'critical')
    render_priority_section('high', issues['high'], '🟠', 'high')
    render_priority_section('medium', issues['medium'], '🟡', 'medium')

    st.markdown("---")
    with st.expander("📄 View Full Roadmap (Markdown)"):
        st.markdown(roadmap)


if __name__ == "__main__":
    main()

# Made with Bob
