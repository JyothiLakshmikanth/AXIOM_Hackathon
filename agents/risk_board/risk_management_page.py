"""
AXIOM Risk Management Page - Streamlit-based Continuous Risk Management
Shows project risks in three big cards (Yesterday/Today/Tomorrow) with expandable details.
Dark theme enforced via .streamlit/config.toml
Run with: streamlit run streamlit_app.py (then navigate to Risk Cockpit tab)
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import logging

# ════════════════════════════════════════════════════════════════════════════════
# STREAMLIT PAGE CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════

# Configure page - theme is handled by .streamlit/config.toml
st.set_page_config(
    page_title="AXIOM | Risk Management",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# COLOR CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════

COLORS = {
    "risk_high": "#e74c3c",
    "risk_medium": "#f39c12",
    "risk_low": "#27ae60",
    "card_bg_yesterday": "rgba(149, 165, 166, 0.08)",
    "card_bg_today": "rgba(243, 156, 18, 0.08)",
    "card_bg_tomorrow": "rgba(41, 128, 185, 0.08)",
    "card_border_yesterday": "#888888",
    "card_border_today": "#f39c12",
    "card_border_tomorrow": "#2980b9",
}

# ════════════════════════════════════════════════════════════════════════════════
# DATA LOADING - LIVE DATA FROM GITHUB ISSUES
# ════════════════════════════════════════════════════════════════════════════════

def get_live_risk_data() -> Dict:
    """Fetch live risk data from GitHub issues.
    
    This function pulls actual data from:
    - GitHub API: Issues (bugs, feature requests, tasks)
    - Calculates risks dynamically based on current state
    - Does NOT use hardcoded snapshots - fully dynamic
    """
    try:
        import requests
        import os
        
        today = date.today().isoformat()
        
        # GitHub configuration
        github_token = os.getenv("GITHUB_TOKEN", "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")
        github_repo = os.getenv("GITHUB_REPO", "JyothiLakshmikanth/EKey2W")
        
        # Fetch LIVE GitHub issues
        all_issues = []
        try:
            response = requests.get(
                f"https://api.github.com/repos/{github_repo}/issues?state=all&per_page=100",
                headers={"Authorization": f"token {github_token}"},
                timeout=10
            )
            if response.status_code == 200:
                all_issues = response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch GitHub issues: {str(e)}")
            all_issues = []
        
        # Convert to DataFrame for easier analysis
        issues_df = pd.DataFrame(all_issues) if all_issues else pd.DataFrame()
        
        # Identify critical/high priority issues
        critical_issues = []
        if not issues_df.empty:
            # Filter for open issues - check both labels AND title keywords
            for _, issue in issues_df.iterrows():
                # Check if issue is still open
                is_open = issue.get("state") == "open"
                
                # Extract labels for priority
                labels = [label.get("name", "").lower() for label in issue.get("labels", [])] if issue.get("labels") else []
                
                # Check title for risk keywords
                title = issue.get("title", "").lower()
                risk_keywords = ["critical", "blocker", "urgent", "constraint", "bottleneck", "failure", "crash", "security", "vulnerability"]
                has_risk_keyword = any(keyword in title for keyword in risk_keywords)
                
                # Issue is critical if it has priority label OR risk keyword in title
                is_critical = has_risk_keyword or any(priority in labels for priority in ["critical", "high", "bug", "security"])
                
                if is_open and is_critical:
                    assignee = issue.get("assignee")
                    assignee_name = assignee.get("login") if assignee else "Unassigned"
                    
                    critical_issues.append({
                        "rank": len(critical_issues) + 1,
                        "title": issue.get("title", "Unknown Issue"),
                        "likelihood": "high" if any(k in title for k in ["critical", "blocker", "urgent"]) or "critical" in labels else "medium",
                        "summary": f"Status: Open, Labels: {', '.join(labels) if labels else 'none'}",
                        "evidence": f"GitHub #{issue.get('number', 'N/A')}, Assignee: {assignee_name}",
                        "rca": {
                            "root_cause_category": "GitHub Issue",
                            "root_cause_detail": f"Issue #{issue.get('number', 'N/A')}: {issue.get('title', 'Unknown')}"
                        },
                        "linked_requirements": labels,
                        "recommended_action": f"Resolve GitHub #{issue.get('number', 'issue')}: {issue.get('title', 'issue')}"
                    })
        
        # Identify high-activity areas (potential risk areas) - sample by issue count ranges
        risk_areas = []
        if not issues_df.empty:
            # Group by first part of title (before -)
            title_categories = {}
            for _, issue in issues_df.iterrows():
                if issue.get("state") == "open":
                    title = issue.get("title", "Unknown")
                    # Extract category from title (e.g., "TWK-120" from "[TWK-120] Some Title")
                    if "[" in title:
                        category = title.split("]")[0] + "]"
                        title_categories[category] = title_categories.get(category, 0) + 1
            
            # Identify concentration areas (3+ issues in same category)
            for category, count in sorted(title_categories.items(), key=lambda x: x[1], reverse=True):
                if count >= 3:
                    risk_areas.append({
                        "rank": len(risk_areas) + 1,
                        "title": f"Active Workstream: {category} ({count} open issues)",
                        "likelihood": "high" if count >= 5 else "medium",
                        "summary": f"Issue category: {category}, Open issues: {count}",
                        "evidence": f"GitHub category: {category}",
                        "rca": {
                            "root_cause_category": "Workload Concentration",
                            "root_cause_detail": f"High concentration of '{category}' issues ({count} open)"
                        },
                        "linked_requirements": [category],
                        "recommended_action": f"Focus on resolving {category} issues"
                    })
        
        # Combine critical issues and risk areas
        features = []
        all_risks = critical_issues + risk_areas
        if all_risks:
            features.append({
                "feature": "Critical GitHub Issues & Risk Areas",
                "delivery_risk": "HIGH" if len(critical_issues) > 2 or any(r["likelihood"] == "high" for r in risk_areas) else "MEDIUM",
                "confidence": "HIGH",
                "top_risks": all_risks[:5]
            })
        
        # Build issue status summary
        open_count = len(issues_df[issues_df["state"] == "open"]) if not issues_df.empty else 0
        closed_count = len(issues_df[issues_df["state"] == "closed"]) if not issues_df.empty else 0
        total_count = len(issues_df) if not issues_df.empty else 0
        
        sprint_risk_data = []
        if total_count > 0:
            sprint_risk_data.append({
                "sprint": "[GITHUB] Issue Status",
                "status": "Off-Track" if open_count > total_count * 0.3 else "At-Risk" if open_count > 0 else "On-Track",
                "planned_vs_capacity": f"{total_count} total issues",
                "defect_inflow_outflow": f"{open_count} open, {closed_count} closed",
                "note": f"GitHub: {open_count}/{total_count} issues open ({round(open_count/total_count*100, 1)}%)"
            })
        
        # Calculate overall delivery risk based on GitHub metrics
        delivery_risk = "HIGH" if (open_count > 10 or len(critical_issues) > 2) else "MEDIUM" if (open_count > 5 or len(critical_issues) > 0) else "LOW"
        
        return {
            "date": today,
            "as_of_date": today,
            "delivery_risk": delivery_risk,
            "overall_confidence": "HIGH",  # HIGH confidence because data is live from GitHub API
            "features": features,
            "sprint_risk": sprint_risk_data,
            "tomorrow_outlook": [
                {
                    "risk": "Continued issue inflow if root causes not addressed",
                    "reason": "Unresolved critical issues block progress in dependent areas",
                    "depends_on": "Priority-based resolution and resource allocation"
                }
            ],
            "is_live_data": True,  # Flag indicating this is live data, not hardcoded
            "data_source": f"GitHub API ({github_repo})"
        }
    
    except Exception as e:
        logger.warning(f"Failed to fetch live risk data: {e}")
        # Fallback to empty snapshot if live data fails
        return {
            "date": date.today().isoformat(),
            "delivery_risk": "MEDIUM",
            "overall_confidence": "MEDIUM",
            "as_of_date": date.today().isoformat(),
            "features": [],
            "sprint_risk": [],
            "tomorrow_outlook": [],
            "is_live_data": False,
            "data_source": "Fallback (live data unavailable)"
        }

def get_today_snapshot() -> Dict:
    """Get today's risk snapshot - fetches LIVE data from GitHub API."""
    return get_live_risk_data()

def get_prior_snapshot() -> Optional[Dict]:
    """Get prior snapshot - returns None (we only show current live data)."""
    return None

# ════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════

def get_risk_icon(level: str) -> str:
    """Get emoji icon for risk level."""
    level_lower = str(level).lower()
    if "high" in level_lower or "critical" in level_lower:
        return "🔴"
    elif "medium" in level_lower:
        return "🟡"
    return "🟢"

def get_risk_color(level: str) -> str:
    """Get color for risk level."""
    level_lower = str(level).lower()
    if "high" in level_lower or "critical" in level_lower:
        return COLORS["risk_high"]
    elif "medium" in level_lower:
        return COLORS["risk_medium"]
    return COLORS["risk_low"]

# ════════════════════════════════════════════════════════════════════════════════
# KPI METRICS SECTION
# ════════════════════════════════════════════════════════════════════════════════

def render_kpis(today_risk: Dict):
    """Render KPI metrics at the top."""
    is_live = today_risk.get("is_live_data", False)
    data_source = today_risk.get("data_source", "Unknown")
    
    if is_live:
        st.markdown("### 📊 Key Performance Indicators (LIVE DATA - Auto-Updated from GitHub)")
        st.caption(f"🔄 Real-time data: {data_source} | Updated: {today_risk.get('as_of_date', 'now')}")
    else:
        st.markdown("### 📊 Key Performance Indicators")
        st.caption("⚠️ Data source unavailable - showing fallback data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        critical_count = sum(len(f.get("top_risks", [])) for f in today_risk.get("features", []) 
                            if f.get("delivery_risk", "").upper() == "HIGH")
        st.metric("🔴 Critical Risks", critical_count)
    
    with col2:
        open_items = sum(1 for risk in today_risk.get("sprint_risk", []) if "open" in str(risk.get("defect_inflow_outflow", "")).lower())
        st.metric("📋 Open Items", open_items)
    
    with col3:
        # Count unique risks across all features
        all_risks = []
        for f in today_risk.get("features", []):
            all_risks.extend(f.get("top_risks", []))
        st.metric("🎯 Top Risks", len(all_risks))
    
    with col4:
        confidence = today_risk.get("overall_confidence", "—")
        st.metric("✅ Confidence", str(confidence).upper())

# ════════════════════════════════════════════════════════════════════════════════
# THREE BIG CARDS - Yesterday/Today/Tomorrow
# ════════════════════════════════════════════════════════════════════════════════

def render_card_header(title: str, date_str: str, risk_level: str, confidence: str = None,
                      bg_color: str = None, border_color: str = None):
    """Render a card header."""
    icon = "🕐" if "Yesterday" in title else ("📍" if "Today" in title else "🔮")
    
    html = f"""
    <div style="
        background-color: {bg_color};
        border-left: 5px solid {border_color};
        border-radius: 10px 10px 0 0;
        padding: 14px 18px;
    ">
        <div style="font-weight: 600; font-size: 15px; margin-bottom: 6px;">
            {icon}  {title} · {date_str}
        </div>
        <div style="font-size: 12px; color: #b0b8c1;">
            Risk: <span style="color: {get_risk_color(risk_level)}; font-weight: 600;">
            {str(risk_level).upper()}</span>
            {f'  ·  Confidence: <span style="color: #27ae60; font-weight: 600;">{str(confidence).upper()}</span>' if confidence else ''}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_risk_button(risk: Dict) -> str:
    """Format risk item for button display."""
    title = risk.get("title", "Untitled")
    if len(title) > 65:
        title = title[:62] + "..."
    icon = get_risk_icon(risk.get("likelihood", "medium"))
    return f"{icon}  {title}"

def render_pluck_cards(today_risk: Dict, prior_risk: Optional[Dict]):
    """Render the three big cards (Yesterday/Today/Tomorrow)."""
    st.markdown("## 📈 Risk Posture Timeline")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # YESTERDAY CARD
    # ─────────────────────────────────────────────────────────────────────────────
    with col1:
        if prior_risk:
            y_date = prior_risk.get("date", "—")
            y_risk = prior_risk.get("delivery_risk", "—")
            try:
                gap_days = (date.today() - date.fromisoformat(y_date)).days
                y_label = f"Last Assessment ({gap_days} days ago)" if gap_days > 1 else "Yesterday"
            except:
                y_label = "Last Assessment"
        else:
            y_date, y_risk, y_label = "—", "—", "No Prior Data"
        
        render_card_header(
            y_label, y_date, y_risk,
            bg_color=COLORS["card_bg_yesterday"],
            border_color=COLORS["card_border_yesterday"]
        )
        
        with st.container(height=400, border=False):
            if prior_risk:
                for i, feature in enumerate(prior_risk.get("features", [])[:2]):
                    for j, risk in enumerate(feature.get("top_risks", [])[:3]):
                        label = render_risk_button(risk)
                        if st.button(label, key=f"y_{i}_{j}", use_container_width=True):
                            st.session_state.selected_risk = risk
            else:
                st.caption("No prior snapshot")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # TODAY CARD
    # ─────────────────────────────────────────────────────────────────────────────
    with col2:
        today_date = today_risk.get("as_of_date", str(date.today()))
        today_risk_level = today_risk.get("delivery_risk", "MEDIUM")
        today_confidence = today_risk.get("overall_confidence", "MEDIUM")
        
        render_card_header(
            "Today", today_date, today_risk_level, today_confidence,
            bg_color=COLORS["card_bg_today"],
            border_color=COLORS["card_border_today"]
        )
        
        with st.container(height=400, border=False):
            today_risks = []
            for feature in today_risk.get("features", []):
                today_risks.extend(feature.get("top_risks", []))
            
            if today_risks:
                for i, risk in enumerate(today_risks[:5]):
                    label = render_risk_button(risk)
                    if st.button(label, key=f"t_{i}", use_container_width=True):
                        st.session_state.selected_risk = risk
            else:
                st.caption("No risks today")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # TOMORROW CARD
    # ─────────────────────────────────────────────────────────────────────────────
    with col3:
        render_card_header(
            "Tomorrow", "Projected", "MEDIUM",
            bg_color=COLORS["card_bg_tomorrow"],
            border_color=COLORS["card_border_tomorrow"]
        )
        
        with st.container(height=400, border=False):
            outlook = today_risk.get("tomorrow_outlook", [])
            if outlook:
                for i, item in enumerate(outlook[:5]):
                    risk_text = item.get("risk", "Unknown")
                    if len(risk_text) > 65:
                        risk_text = risk_text[:62] + "..."
                    label = f"🔮  {risk_text}"
                    if st.button(label, key=f"tm_{i}", use_container_width=True):
                        st.session_state.selected_outlook = item
            else:
                st.caption("No projected risks")

# ════════════════════════════════════════════════════════════════════════════════
# RISK DETAIL PANELS
# ════════════════════════════════════════════════════════════════════════════════

def render_risk_detail():
    """Show detailed view of selected risk."""
    if "selected_risk" in st.session_state and st.session_state.selected_risk:
        risk = st.session_state.selected_risk
        st.markdown("---")
        st.markdown(f"### 🔍 Risk Detail: {risk.get('title', 'Risk')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Likelihood:** {risk.get('likelihood', '—').upper()}")
        with col2:
            st.markdown(f"**Rank:** #{risk.get('rank', '—')}")
        with col3:
            confidence = risk.get("confidence", "—")
            st.markdown(f"**Confidence:** {str(confidence).upper()}")
        
        st.markdown(f"**Summary:** {risk.get('summary', 'N/A')}")
        st.markdown(f"**Evidence:** {risk.get('evidence', 'N/A')}")
        
        rca = risk.get("rca", {}) or {}
        if rca:
            st.markdown(f"**Root Cause:** {rca.get('root_cause_category', 'Unknown')}")
            if rca.get('root_cause_detail'):
                st.markdown(f"*{rca.get('root_cause_detail')}*")
        
        if risk.get("linked_requirements"):
            st.markdown(f"**Requirements:** {', '.join(risk['linked_requirements'])}")
        
        if risk.get("recommended_action"):
            st.warning(f"**Action:** {risk['recommended_action']}")
    
    elif "selected_outlook" in st.session_state and st.session_state.selected_outlook:
        outlook = st.session_state.selected_outlook
        st.markdown("---")
        st.markdown("### 🔮 Projected Risk")
        st.markdown(f"**Risk:** {outlook.get('risk', '—')}")
        st.markdown(f"**Reason:** {outlook.get('reason', '—')}")
        st.markdown(f"**Depends On:** {outlook.get('depends_on', '—')}")

# ════════════════════════════════════════════════════════════════════════════════
# TOP RISKS BY FEATURE
# ════════════════════════════════════════════════════════════════════════════════

def render_top_risks_by_feature(today_risk: Dict):
    """Render top risks grouped by feature/team."""
    st.markdown("## 🎯 Top Risks by Feature/Team")
    
    features = today_risk.get("features", [])
    if not features:
        st.info("No feature data")
        return
    
    for feature in features:
        fname = feature.get("feature", "Unknown")
        frisk = feature.get("delivery_risk", "MEDIUM")
        fconfidence = feature.get("confidence", "MEDIUM")
        
        with st.expander(f"{get_risk_icon(frisk)} {fname} — {str(frisk).upper()}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Delivery Risk:** {str(frisk).upper()}")
            with col2:
                st.markdown(f"**Confidence:** {str(fconfidence).upper()}")
            
            for risk in feature.get("top_risks", []):
                st.markdown(f"**{risk.get('title', 'Risk')}**")
                st.markdown(f"- Likelihood: {risk.get('likelihood', '—')}")
                st.markdown(f"- Evidence: {risk.get('evidence', '—')}")
                if risk.get('recommended_action'):
                    st.info(risk.get('recommended_action'))
                st.divider()

# ════════════════════════════════════════════════════════════════════════════════
# SPRINT RISK TABLE
# ════════════════════════════════════════════════════════════════════════════════

def render_sprint_risk_table(today_risk: Dict):
    """Render sprint risk table."""
    sprint_risks = today_risk.get("sprint_risk", [])
    
    if not sprint_risks:
        st.info("No sprint data")
        return
    
    st.markdown("## 📅 Sprint Risk Assessment")
    
    rows = []
    for row in sprint_risks:
        rows.append({
            "Sprint": row.get("sprint", "—"),
            "Status": row.get("status", "—"),
            "Planned vs Capacity": row.get("planned_vs_capacity", "—"),
            "Defect Flow": row.get("defect_inflow_outflow", "—"),
        })
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════════
# MAIN PAGE FUNCTION
# ════════════════════════════════════════════════════════════════════════════════

def render_risk_management_page():
    """Main risk management page function (called from streamlit_app.py)."""
    
    # Initialize session state
    if "selected_risk" not in st.session_state:
        st.session_state.selected_risk = None
    if "selected_outlook" not in st.session_state:
        st.session_state.selected_outlook = None
    
    # Load snapshots
    today = get_today_snapshot()
    prior = get_prior_snapshot()
    
    # Header
    st.markdown("# ⚠️ AXIOM Risk Management")
    st.markdown("Evidence-Driven Continuous Risk Assessment")
    
    # KPIs
    st.divider()
    render_kpis(today)
    
    # Three cards
    st.divider()
    render_pluck_cards(today, prior)
    
    # Risk detail
    render_risk_detail()
    
    # Top risks by feature
    st.divider()
    render_top_risks_by_feature(today)
    
    # Sprint table
    st.divider()
    render_sprint_risk_table(today)


class RiskAnalyzer:
    """Analyzes project risks based on defects, capacity, and resource constraints."""
    
    def __init__(self, data_dir: str):
        """Initialize risk analyzer with data directory."""
        self.data_dir = Path(data_dir)
        self.jira_data = None
        self.capacity_data = None
        self.competency_data = None
        self.pi_data = None
        self.risks = []
        self.load_data()
    
    def load_data(self):
        """Load all required CSV data files."""
        try:
            # Load JIRA issues including bugs and tasks
            jira_path = self.data_dir / "jira_issues.csv"
            if jira_path.exists():
                self.jira_data = pd.read_csv(jira_path)
            
            # Load capacity planning
            capacity_path = self.data_dir / "AXIOM_Capacity_Planning.csv"
            if capacity_path.exists():
                self.capacity_data = pd.read_csv(capacity_path)
            
            # Load competency matrix
            competency_path = self.data_dir / "AXIOM_Competency_Matrix.csv"
            if competency_path.exists():
                self.competency_data = pd.read_csv(competency_path)
            
            # Load PI planning
            pi_path = self.data_dir / "AXIOM_PI_Planning_2026.csv"
            if pi_path.exists():
                self.pi_data = pd.read_csv(pi_path)
                
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def analyze_critical_defects(self) -> List[Dict]:
        """Identify and analyze critical and open defects."""
        defects = []
        
        if self.jira_data is None:
            return defects
        
        # Filter for bugs and critical/high priority items
        critical_items = self.jira_data[
            (self.jira_data['Type'].isin(['Bug', 'Defect'])) |
            (self.jira_data['Priority'].isin(['Critical', 'High']))
        ]
        
        for _, item in critical_items.iterrows():
            defect = {
                'id': item.get('Issue Key', 'N/A'),
                'summary': item.get('Summary', 'N/A'),
                'type': item.get('Type', 'Unknown'),
                'status': item.get('Status', 'Unknown'),
                'priority': item.get('Priority', 'Unknown'),
                'assignee': item.get('Assignee', 'Unassigned'),
                'sprint': item.get('Sprint', 'N/A'),
                'impact': self._assess_impact(item),
                'mitigation': self._suggest_mitigation(item)
            }
            defects.append(defect)
        
        return defects
    
    def analyze_resource_constraints(self) -> Dict:
        """Analyze resource allocation and identify bottlenecks."""
        constraints = {}
        
        if self.capacity_data is None:
            return constraints
        
        # Identify resources with high allocation (>80%)
        high_allocation = self.capacity_data[
            self.capacity_data['Allocation_%'] > 80
        ]
        
        for _, resource in high_allocation.iterrows():
            resource_id = resource.get('Resource_ID', 'Unknown')
            constraints[resource_id] = {
                'name': resource.get('Associate', 'Unknown'),
                'role': resource.get('Role', 'N/A'),
                'domain': resource.get('Domain', 'N/A'),
                'allocation': resource.get('Allocation_%', 0),
                'location': resource.get('Location', 'N/A'),
                'risk_level': 'High' if resource.get('Allocation_%', 0) >= 100 else 'Medium',
                'recommendations': self._resource_recommendations(resource)
            }
        
        return constraints
    
    def analyze_domain_risks(self) -> Dict:
        """Analyze risks by technical domain."""
        domain_risks = defaultdict(lambda: {
            'open_defects': 0,
            'critical_items': 0,
            'assigned_resources': [],
            'capacity_status': 'Unknown'
        })
        
        if self.jira_data is None:
            return domain_risks
        
        # Map issue assignees to domains
        for _, issue in self.jira_data.iterrows():
            assignee = issue.get('Assignee', 'Unknown')
            issue_type = issue.get('Type', 'Unknown')
            priority = issue.get('Priority', 'Unknown')
            status = issue.get('Status', 'Unknown')
            
            # Find domain from competency data if available
            domain = self._find_resource_domain(assignee)
            
            if status in ['Open', 'In Progress']:
                domain_risks[domain]['open_defects'] += 1
            
            if priority == 'Critical':
                domain_risks[domain]['critical_items'] += 1
            
            if assignee != 'Unknown' and assignee not in domain_risks[domain]['assigned_resources']:
                domain_risks[domain]['assigned_resources'].append(assignee)
        
        return dict(domain_risks)
    
    def analyze_sprint_risks(self) -> List[Dict]:
        """Analyze risks at sprint level."""
        sprint_risks = []
        
        if self.jira_data is None:
            return sprint_risks
        
        sprints = self.jira_data['Sprint'].unique()
        
        for sprint in sprints:
            if pd.isna(sprint):
                continue
                
            sprint_issues = self.jira_data[self.jira_data['Sprint'] == sprint]
            
            open_count = len(sprint_issues[sprint_issues['Status'].isin(['Open', 'In Progress'])])
            critical_count = len(sprint_issues[sprint_issues['Priority'] == 'Critical'])
            
            risk_level = self._calculate_sprint_risk(sprint_issues)
            
            sprint_risks.append({
                'sprint_id': sprint,
                'total_items': len(sprint_issues),
                'open_items': open_count,
                'critical_items': critical_count,
                'risk_level': risk_level,
                'focus_areas': self._identify_focus_areas(sprint_issues)
            })
        
        return sprint_risks
    
    def generate_risk_report(self) -> Dict:
        """Generate comprehensive risk management report."""
        report = {
            'generated_date': datetime.now().isoformat(),
            'project': 'AXIOM E-Key 2W',
            'summary': {
                'overall_risk_level': 'Medium',
                'critical_defects': 0,
                'resource_bottlenecks': 0,
                'at_risk_sprints': 0
            },
            'critical_defects': self.analyze_critical_defects(),
            'resource_constraints': self.analyze_resource_constraints(),
            'domain_risks': self.analyze_domain_risks(),
            'sprint_risks': self.analyze_sprint_risks(),
            'mitigation_strategies': self._generate_mitigations()
        }
        
        # Calculate summary metrics
        report['summary']['critical_defects'] = len([d for d in report['critical_defects'] 
                                                      if d['priority'] == 'Critical'])
        report['summary']['resource_bottlenecks'] = len(report['resource_constraints'])
        report['summary']['at_risk_sprints'] = len([s for s in report['sprint_risks'] 
                                                     if s['risk_level'] in ['High', 'Critical']])
        
        return report
    
    def _assess_impact(self, item: pd.Series) -> str:
        """Assess the business impact of a defect."""
        priority = item.get('Priority', 'Medium')
        summary = str(item.get('Summary', '')).lower()
        
        if priority == 'Critical' or 'security' in summary or 'boundary' in summary:
            return 'High'
        elif priority == 'High' or 'latency' in summary:
            return 'Medium'
        else:
            return 'Low'
    
    def _suggest_mitigation(self, item: pd.Series) -> str:
        """Suggest mitigation strategy for a defect."""
        summary = str(item.get('Summary', '')).lower()
        
        if 'security' in summary:
            return 'Prioritize security review and patching'
        elif 'latency' in summary:
            return 'Performance optimization task required'
        elif 'boundary' in summary:
            return 'Edge case testing and validation needed'
        else:
            return 'Standard defect resolution process'
    
    def _resource_recommendations(self, resource: pd.Series) -> List[str]:
        """Generate recommendations for high-allocation resources."""
        allocation = resource.get('Allocation_%', 0)
        recommendations = []
        
        if allocation >= 100:
            recommendations.append('Consider task redistribution')
            recommendations.append('Monitor for burnout and quality issues')
        elif allocation >= 90:
            recommendations.append('Limit new assignments')
            recommendations.append('Monitor capacity closely')
        
        return recommendations
    
    def _find_resource_domain(self, assignee: str) -> str:
        """Find the domain of a resource from competency data."""
        if self.competency_data is None or not assignee or assignee == 'Unknown':
            return 'Unknown'
        
        resource_data = self.competency_data[
            self.competency_data['associate'] == assignee
        ]
        
        if not resource_data.empty:
            return resource_data.iloc[0]['domain']
        
        return 'Unknown'
    
    def _calculate_sprint_risk(self, sprint_issues: pd.DataFrame) -> str:
        """Calculate overall risk level for a sprint."""
        critical_pct = len(sprint_issues[sprint_issues['Priority'] == 'Critical']) / len(sprint_issues) * 100
        open_pct = len(sprint_issues[sprint_issues['Status'].isin(['Open'])]) / len(sprint_issues) * 100
        
        if critical_pct > 20 or open_pct > 30:
            return 'Critical'
        elif critical_pct > 10 or open_pct > 15:
            return 'High'
        elif critical_pct > 5 or open_pct > 10:
            return 'Medium'
        else:
            return 'Low'
    
    def _identify_focus_areas(self, sprint_issues: pd.DataFrame) -> List[str]:
        """Identify key focus areas for a sprint based on issues."""
        focus = []
        
        if len(sprint_issues[sprint_issues['Priority'] == 'Critical']) > 0:
            focus.append('Critical items resolution')
        
        if len(sprint_issues[sprint_issues['Type'] == 'Bug']) > 0:
            focus.append('Defect fixing')
        
        if len(sprint_issues[sprint_issues['Status'] == 'In Progress']) > len(sprint_issues) / 2:
            focus.append('Completion acceleration')
        
        return focus if focus else ['Regular feature development']
    
    def _generate_mitigations(self) -> Dict:
        """Generate comprehensive mitigation strategies."""
        return {
            'resource_management': [
                'Balance workload across teams',
                'Cross-train team members for critical skills',
                'Prioritize security engineer allocation for Sprints 4-5',
                'Plan QA capacity expansion before Alpha exit'
            ],
            'defect_management': [
                'Implement boundary-zone testing protocol',
                'Add low-power phone validation to test matrix',
                'Establish revocation cache invalidation process',
                'Deploy security event audit logging'
            ],
            'schedule_management': [
                'Buffer time in PI-2 for latency optimization',
                'Pre-allocate security resources for PI-3',
                'Front-load QA activities in PI-2 and PI-3',
                'Plan release hardening activities early in PI-4'
            ],
            'technical_mitigations': [
                'Implement robust proximity decision algorithm',
                'Add firmware cache invalidation hooks',
                'Enhance security audit trail capabilities',
                'Develop offline synchronization mechanism'
            ]
        }
    
    def export_report(self, output_path: str):
        """Export risk report to JSON file."""
        report = self.generate_risk_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Risk report exported to {output_path}")
    
    def print_summary(self):
        """Print risk summary to console."""
        report = self.generate_risk_report()
        
        print("\n" + "="*80)
        print("AXIOM E-Key 2W PROJECT RISK MANAGEMENT REPORT")
        print("="*80)
        print(f"Generated: {report['generated_date']}")
        print(f"\nRISK SUMMARY:")
        print(f"  Overall Risk Level: {report['summary']['overall_risk_level']}")
        print(f"  Critical Defects: {report['summary']['critical_defects']}")
        print(f"  Resource Bottlenecks: {report['summary']['resource_bottlenecks']}")
        print(f"  At-Risk Sprints: {report['summary']['at_risk_sprints']}")
        
        print(f"\nCRITICAL DEFECTS ({len(report['critical_defects'])}):")
        for defect in report['critical_defects'][:5]:  # Top 5
            print(f"  - {defect['id']}: {defect['summary']}")
            print(f"    Status: {defect['status']}, Assignee: {defect['assignee']}")
            print(f"    Impact: {defect['impact']}")
        
        print(f"\nRESOURCE CONSTRAINTS:")
        for resource_id, constraint in list(report['resource_constraints'].items())[:5]:
            print(f"  - {resource_id} ({constraint['name']}): {constraint['allocation']}%")
            print(f"    Risk Level: {constraint['risk_level']}")
        
        print(f"\nDOMAIN RISKS:")
        for domain, risks in report['domain_risks'].items():
            print(f"  - {domain}: {risks['open_defects']} open, {risks['critical_items']} critical")
        
        print("\n" + "="*80 + "\n")


class RiskDashboardAPI:
    """Flask API for risk management dashboard and querying."""
    
    def __init__(self, analyzer: RiskAnalyzer, port: int = 5000):
        """Initialize dashboard API with risk analyzer."""
        self.app = Flask(__name__)
        CORS(self.app)
        self.analyzer = analyzer
        self.port = port
        self.logger = logging.getLogger(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for risk management API."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'healthy', 'service': 'Risk Management Dashboard'})
        
        @self.app.route('/api/risk-summary', methods=['GET'])
        def risk_summary():
            """Get overall risk summary."""
            report = self.analyzer.generate_risk_report()
            return jsonify(report['summary'])
        
        @self.app.route('/api/critical-defects', methods=['GET'])
        def critical_defects():
            """Get critical defects with optional filtering."""
            priority = request.args.get('priority', 'all').upper()
            status = request.args.get('status', 'all').upper()
            domain = request.args.get('domain', 'all').upper()
            
            defects = self.analyzer.analyze_critical_defects()
            
            # Apply filters
            if priority != 'ALL':
                defects = [d for d in defects if d['priority'].upper() == priority]
            if status != 'ALL':
                defects = [d for d in defects if d['status'].upper() == status]
            
            return jsonify({
                'total_count': len(defects),
                'defects': defects
            })
        
        @self.app.route('/api/resource-constraints', methods=['GET'])
        def resource_constraints():
            """Get resource constraints and bottlenecks."""
            allocation_threshold = request.args.get('threshold', 80, type=int)
            
            constraints = self.analyzer.analyze_resource_constraints()
            
            return jsonify({
                'total_constrained': len(constraints),
                'threshold_percent': allocation_threshold,
                'resources': constraints
            })
        
        @self.app.route('/api/domain-risks', methods=['GET'])
        def domain_risks():
            """Get risks by technical domain."""
            domain = request.args.get('domain', None)
            
            risks = self.analyzer.analyze_domain_risks()
            
            if domain and domain in risks:
                return jsonify({domain: risks[domain]})
            
            return jsonify(risks)
        
        @self.app.route('/api/sprint-risks', methods=['GET'])
        def sprint_risks():
            """Get sprint-level risk analysis."""
            sprint_id = request.args.get('sprint_id', None)
            risk_level = request.args.get('risk_level', 'all').upper()
            
            risks = self.analyzer.analyze_sprint_risks()
            
            if sprint_id:
                risks = [r for r in risks if r['sprint_id'] == sprint_id]
            
            if risk_level != 'ALL':
                risks = [r for r in risks if r['risk_level'].upper() == risk_level]
            
            return jsonify({
                'total_sprints': len(risks),
                'sprints': risks
            })
        
        @self.app.route('/api/mitigation-strategies', methods=['GET'])
        def mitigation_strategies():
            """Get mitigation strategies for identified risks."""
            report = self.analyzer.generate_risk_report()
            return jsonify(report['mitigation_strategies'])
        
        @self.app.route('/api/risk-query', methods=['POST'])
        def risk_query():
            """Advanced risk query with custom filters."""
            query_params = request.get_json() or {}
            
            response = {
                'query_timestamp': datetime.now().isoformat(),
                'filters_applied': query_params,
                'results': {}
            }
            
            # Analyze defects if requested
            if query_params.get('include_defects', False):
                defects = self.analyzer.analyze_critical_defects()
                if query_params.get('defect_priority'):
                    defects = [d for d in defects 
                              if d['priority'].upper() == query_params['defect_priority'].upper()]
                response['results']['defects'] = defects
            
            # Analyze resources if requested
            if query_params.get('include_resources', False):
                resources = self.analyzer.analyze_resource_constraints()
                response['results']['resources'] = resources
            
            # Analyze domains if requested
            if query_params.get('include_domains', False):
                domains = self.analyzer.analyze_domain_risks()
                response['results']['domains'] = domains
            
            # Analyze sprints if requested
            if query_params.get('include_sprints', False):
                sprints = self.analyzer.analyze_sprint_risks()
                response['results']['sprints'] = sprints
            
            # Generate mitigation strategies
            if query_params.get('include_mitigations', False):
                full_report = self.analyzer.generate_risk_report()
                response['results']['mitigations'] = full_report['mitigation_strategies']
            
            # If no specific analysis requested, return full report
            if not response['results']:
                response['results'] = self.analyzer.generate_risk_report()
            
            return jsonify(response)
        
        @self.app.route('/api/full-report', methods=['GET'])
        def full_report():
            """Get complete risk management report."""
            report = self.analyzer.generate_risk_report()
            return jsonify(report)
        
        @self.app.route('/api/risk-score', methods=['GET'])
        def risk_score():
            """Calculate overall project risk score (0-100)."""
            report = self.analyzer.generate_risk_report()
            summary = report['summary']
            
            # Risk scoring logic
            defect_score = min(summary.get('critical_defects', 0) * 5, 40)
            resource_score = min(summary.get('resource_bottlenecks', 0) * 3, 30)
            sprint_score = min(summary.get('at_risk_sprints', 0) * 4, 30)
            
            total_score = defect_score + resource_score + sprint_score
            
            risk_level = 'Low' if total_score < 30 else 'Medium' if total_score < 60 else 'High'
            
            return jsonify({
                'overall_score': total_score,
                'risk_level': risk_level,
                'component_scores': {
                    'defects': defect_score,
                    'resources': resource_score,
                    'sprints': sprint_score
                },
                'recommendation': self._score_recommendation(total_score)
            })
        
        @self.app.errorhandler(400)
        def bad_request(error):
            """Handle bad request errors."""
            return jsonify({'error': 'Bad request', 'message': str(error)}), 400
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle not found errors."""
            return jsonify({'error': 'Not found', 'message': str(error)}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle internal server errors."""
            self.logger.error(f"Internal error: {error}")
            return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
    
    def _score_recommendation(self, score: float) -> str:
        """Generate recommendation based on risk score."""
        if score < 20:
            return "Project is healthy. Continue monitoring."
        elif score < 40:
            return "Minor risks detected. Increase monitoring frequency."
        elif score < 60:
            return "Moderate risks identified. Implement mitigation strategies."
        elif score < 80:
            return "High risks present. Escalate to project leadership."
        else:
            return "Critical risks identified. Immediate action required."
    
    def run(self, debug: bool = False):
        """Start Flask development server."""
        logging.basicConfig(level=logging.INFO)
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)
    
    def get_app(self):
        """Get Flask app instance for production deployment."""
        return self.app


# ════════════════════════════════════════════════════════════════════════════════
# STREAMLIT ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    render_risk_management_page()

def main():
    """Main function to run risk analysis and dashboard API."""
    import sys
    
    # Set data directory to AXIOM project data folder
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Create analyzer
    analyzer = RiskAnalyzer(str(data_dir))
    
    # Check if running as API server or CLI
    if '--api' in sys.argv or '--server' in sys.argv:
        # Start Flask API server
        port = 5000
        if '--port' in sys.argv:
            port_idx = sys.argv.index('--port') + 1
            if port_idx < len(sys.argv):
                port = int(sys.argv[port_idx])
        
        print(f"Starting Risk Management Dashboard API on port {port}...")
        api = RiskDashboardAPI(analyzer, port=port)
        api.run(debug=False)
    else:
        # Run CLI mode
        print("Running in CLI mode. Use --api flag to start API server.")
        analyzer.print_summary()
        
        # Export full report
        output_file = Path(__file__).parent / "risk_analysis_report.json"
        analyzer.export_report(str(output_file))
    
    return analyzer


# if __name__ == "__main__":
#     main()
