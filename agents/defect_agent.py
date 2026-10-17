"""
Defect & Issue Intelligence Specialist Agent.
Implemented as a specialized LangChain ReAct agent querying JIRA issue facts,
scoring defect severity/urgency, and classifying leakage directions.
Now integrates with real data from AXIOM-main repository.
"""

import json
import logging
import os
import csv
import requests
from io import StringIO
from typing import Dict, Any, List, Optional
from agents.tools.firestore_tools import firestore_get_cached_evidence

logger = logging.getLogger("axiom.agents.defect")

SYSTEM_PROMPT = """You are the Defect Intelligence Specialist Agent for AXIOM.
Your mission is to query JIRA issue records and defect queues, calculate severity and urgency scores,
and classify probable leakage directions for Master triage.

Available Tools:
- load_defects_from_repository(sprint_id: str, issue_key: str)
- analyze_defect_severity_urgency(defect_record: dict)

Rules:
1. Always ground your triage findings in authoritative JIRA tracker records.
2. You CANNOT declare root causes without engineering code inspection evidence.
3. You CANNOT close issues or modify issue states without human authorization.
"""


def load_jira_issues_from_csv() -> Dict[str, Dict[str, Any]]:
    """Load JIRA issues from GitHub repository data."""
    github_url = "https://raw.githubusercontent.com/JyothiLakshmikanth/AXIOM-main/main/data/jira_issues.csv"
    
    # Fallback local paths
    local_paths = [
        r"C:\New folder\builder_axoim\AXIOM-main\data\jira_issues.csv",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "..", "builder_axoim", "AXIOM-main", "data", "jira_issues.csv"
        ),
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "builder_axoim", "AXIOM-main", "data", "jira_issues.csv"
        )
    ]
    
    issues = {}
    
    # Try GitHub URL first
    try:
        response = requests.get(github_url, timeout=10)
        response.raise_for_status()
        reader = csv.DictReader(StringIO(response.text))
        for row in reader:
            issue_key = row.get("Issue Key", "")
            if issue_key:
                issues[issue_key] = row
        logger.info(f"Loaded {len(issues)} JIRA issues from GitHub: {github_url}")
        return issues
    except Exception as e:
        logger.warning(f"Failed to fetch from GitHub ({e}). Trying local paths...")
    
    # Fallback to local paths
    for repo_path in local_paths:
        if os.path.exists(repo_path):
            try:
                with open(repo_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        issue_key = row.get("Issue Key", "")
                        if issue_key:
                            issues[issue_key] = row
                    logger.info(f"Loaded {len(issues)} JIRA issues from local: {repo_path}")
                    return issues
            except Exception as e:
                logger.error(f"Error loading from {repo_path}: {e}")
    
    logger.warning("Could not load JIRA issues from GitHub or local paths")
    return issues


class DefectAgent:
    """Specialized LangChain ReAct Agent for Defect Intelligence."""

    def __init__(self):
        self.agent_id = "defect_agent"
        self.name = "Defect Intelligence Specialist Agent"
        self.jira_issues = load_jira_issues_from_csv()

    def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes autonomous ReAct reasoning loop:
        Thought -> Action -> Observation -> Final Evidence Synthesis.
        """
        issue_id = task_input.get("issue_id")
        sprint_id = task_input.get("sprint_id")
        action = task_input.get("action", "triage_issue")

        evidences = []
        findings = {}

        # If issue_id not provided, try to extract from query or use sprint-based search
        if not issue_id:
            if sprint_id:
                # Find all open defects in sprint
                defects = self._get_defects_by_sprint(sprint_id)
                if defects:
                    issue_id = list(defects.keys())[0]  # Get first defect
            if not issue_id and self.jira_issues:
                # Find any open critical defect
                for key, issue in self.jira_issues.items():
                    if issue.get("Type") == "Bug" and issue.get("Status") == "Open" and issue.get("Priority") in ["Critical", "High"]:
                        issue_id = key
                        break

        # ReAct Step 1: Check runtime memory cache first
        cached = firestore_get_cached_evidence(issue_id) if issue_id else None
        if cached:
            defect_record = cached.get("payload", {})
            evidences.append(cached)
        else:
            # Fetch from JIRA data
            defect_record = self._get_defect_by_id(issue_id) if issue_id else {}
            if defect_record:
                evidences.append({
                    "artifact_id": issue_id,
                    "artifact_type": "jira_issue_record",
                    "source_system": "github_jira_dataset",
                    "source_uri": f"https://raw.githubusercontent.com/JyothiLakshmikanth/AXIOM-main/main/data/jira_issues.csv (Issue: {issue_id})",
                    "version": "1.0",
                    "updated_at": "2026-10-17T08:30:00Z",
                    "authoritative": True,
                    "synthetic": False,
                    "quality_status": "verified",
                    "payload": defect_record
                })

        findings["defect_record"] = defect_record
        findings["total_open_defects"] = self._count_open_defects()
        findings["critical_defects"] = self._get_critical_defects()

        # ReAct Step 2: Reason on Severity, Urgency, and Leakage Direction
        severity, urgency = self._calculate_severity_urgency(defect_record)
        findings["severity"] = severity
        findings["urgency"] = urgency
        findings["leakage_analysis"] = self._analyze_leakage(defect_record)
        findings["impacted_milestone"] = defect_record.get("Milestone", "Unknown")
        findings["assigned_engineer"] = defect_record.get("Assignee", "Unassigned")

        summary = f"Analyzed defect landscape: {findings['total_open_defects']} open defects, {len(findings['critical_defects'])} critical."
        if issue_id and defect_record:
            summary = f"Ingested defect {issue_id} ({defect_record.get('Summary', 'N/A')}). Severity: {severity}, Urgency: {urgency}."

        return {
            "agent_id": self.agent_id,
            "execution_status": "SUCCESS",
            "summary": summary,
            "findings": findings,
            "evidences": evidences
        }

    def _get_defect_by_id(self, issue_id: Optional[str]) -> Dict[str, Any]:
        """Retrieve a specific defect by issue ID."""
        if not issue_id or issue_id not in self.jira_issues:
            return {}
        issue = self.jira_issues[issue_id]
        # Only return bugs that are defects
        if issue.get("Type") == "Bug":
            return issue
        return {}

    def _get_defects_by_sprint(self, sprint_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all defects in a specific sprint."""
        defects = {}
        for key, issue in self.jira_issues.items():
            if issue.get("Type") == "Bug" and issue.get("Sprint") == sprint_id:
                defects[key] = issue
        return defects

    def _count_open_defects(self) -> int:
        """Count total open defects."""
        return sum(1 for issue in self.jira_issues.values() 
                  if issue.get("Type") == "Bug" and issue.get("Status") == "Open")

    def _get_critical_defects(self) -> List[Dict[str, Any]]:
        """Get all critical and high priority open defects."""
        critical = []
        for key, issue in self.jira_issues.items():
            if (issue.get("Type") == "Bug" and issue.get("Status") == "Open" and 
                issue.get("Priority") in ["Critical", "High"]):
                critical.append({
                    "issue_key": key,
                    "summary": issue.get("Summary"),
                    "priority": issue.get("Priority"),
                    "sprint": issue.get("Sprint"),
                    "assignee": issue.get("Assignee")
                })
        return critical

    def _calculate_severity_urgency(self, defect_record: Dict[str, Any]) -> tuple:
        """Calculate severity and urgency scores from defect record."""
        priority = defect_record.get("Priority", "Medium")
        status = defect_record.get("Status", "Open")
        
        severity_map = {
            "Critical": "S1_CRITICAL",
            "High": "S2_HIGH",
            "Medium": "S3_MEDIUM",
            "Low": "S4_LOW"
        }
        severity = severity_map.get(priority, "S3_MEDIUM")
        
        # Urgency depends on status and priority
        if status == "Open" and priority in ["Critical", "High"]:
            urgency = "U1_IMMEDIATE"
        elif status == "In Progress" and priority == "Critical":
            urgency = "U1_IMMEDIATE"
        elif status == "Open":
            urgency = "U2_HIGH"
        else:
            urgency = "U3_NORMAL"
        
        return severity, urgency

    def _analyze_leakage(self, defect_record: Dict[str, Any]) -> str:
        """Analyze probable leakage direction from defect record."""
        summary = defect_record.get("Summary", "").lower()
        description = defect_record.get("Description", "").lower()
        full_text = f"{summary} {description}".lower()
        
        if "unlock" in full_text or "proximity" in full_text:
            return "Proximity Controller Logic (Boundary Condition Missing)"
        elif "latency" in full_text or "performance" in full_text:
            return "Performance Optimization Gap"
        elif "revok" in full_text or "cache" in full_text:
            return "Key Management Caching Logic"
        elif "propag" in full_text:
            return "Data Propagation Pipeline"
        else:
            return "General Implementation Gap"


# Global agent instance
defect_agent = DefectAgent()
