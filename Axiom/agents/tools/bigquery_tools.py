"""
BigQuery Analytics & Structured Project Facts Tools for AXIOM.
Handles:
- Defect queues & GitHub issue records
- Historical sprint velocity & burndown numbers
- Resource capacity allocations & utilization
- Test run results & QA coverage metrics
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("axiom.tools.bigquery")

# Synthetic BigQuery Tables
_BQ_DEFECTS = {
    "GH-ISSUE-107": {
        "issue_id": "GH-ISSUE-107",
        "title": "Proximity boundary oscillation causes rapid lock/unlock chatter at 2.0m",
        "body": "When user stands at approximately 2.0m from vehicle with key fob, proximity controller oscillates between True and False state rapidly, actuating mechanical door lock relay 15 times in 10 seconds.",
        "severity": "S1_CRITICAL",
        "urgency": "U1_IMMEDIATE",
        "sprint_id": "SPRINT-04",
        "status": "OPEN",
        "labels": ["defect", "customer-escalation", "passive-entry"],
        "created_at": "2026-10-04T08:30:00Z"
    }
}

_BQ_SPRINTS = {
    "SPRINT-04": {
        "sprint_id": "SPRINT-04",
        "name": "Sprint 4 - Passive Access Alpha Hardening",
        "start_date": "2026-09-28",
        "end_date": "2026-10-09",
        "working_days_total": 10,
        "working_days_remaining": 3,
        "committed_points": 45,
        "completed_points": 28,
        "carryover_points": 0,
        "historical_sprints": [
            {"sprint": "SPRINT-01", "committed": 40, "completed": 42},
            {"sprint": "SPRINT-02", "committed": 45, "completed": 44},
            {"sprint": "SPRINT-03", "committed": 42, "completed": 39}
        ]
    }
}

_BQ_TEST_RUNS = [
    {
        "test_run_id": "TR-9021",
        "test_id": "TC-004",
        "name": "test_proximity_boundary_oscillation",
        "file": "tests/test_proximity_controller.py",
        "status": "FAILED",
        "failure_log": "AssertionError: Expected stable single unlock event, but received 14 toggle events within 500ms window at distance 2.0m.",
        "execution_date": "2026-10-04T09:15:00Z",
        "branch": "main"
    }
]


def bigquery_get_defect_by_issue_id(issue_id: str) -> Dict[str, Any]:
    """Retrieves authoritative defect details from BigQuery."""
    return _BQ_DEFECTS.get(issue_id, {"error": f"Defect {issue_id} not found."})


def bigquery_list_open_defects_by_sprint(sprint_id: str) -> List[Dict[str, Any]]:
    """Lists open defects impacting a specific sprint."""
    return [d for d in _BQ_DEFECTS.values() if d.get("sprint_id") == sprint_id and d.get("status") == "OPEN"]


def bigquery_get_team_velocity_history(sprint_id: str) -> Dict[str, Any]:
    """Computes rolling velocity and volatility across sprints."""
    sprint_data = _BQ_SPRINTS.get(sprint_id, _BQ_SPRINTS["SPRINT-04"])
    hist = sprint_data.get("historical_sprints", [])
    completed_vals = [h["completed"] for h in hist]
    rolling_avg = sum(completed_vals) / max(1, len(completed_vals))

    # Variance / volatility calculation
    variance = sum((x - rolling_avg) ** 2 for x in completed_vals) / max(1, len(completed_vals))
    std_dev = variance ** 0.5
    volatility = std_dev / max(1.0, rolling_avg)

    return {
        "sprint_id": sprint_id,
        "rolling_average_velocity": round(rolling_avg, 2),
        "volatility_index": round(volatility, 3),
        "current_sprint_committed": sprint_data["committed_points"],
        "current_sprint_completed": sprint_data["completed_points"],
        "days_remaining": sprint_data["working_days_remaining"],
        "slip_risk": "HIGH" if sprint_data["completed_points"] + (rolling_avg * 0.3) < sprint_data["committed_points"] else "LOW"
    }


def bigquery_get_test_run_results(test_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves QA test execution records."""
    if test_id:
        return [tr for tr in _BQ_TEST_RUNS if tr["test_id"] == test_id]
    return _BQ_TEST_RUNS


def bigquery_get_coverage_summary(module_name: str) -> Dict[str, Any]:
    """Retrieves line and branch coverage metrics for target module."""
    if "proximity" in module_name.lower():
        return {
            "module": module_name,
            "line_coverage_pct": 82.5,
            "branch_coverage_pct": 58.0,
            "uncovered_boundary_branches": [
                "proximity_controller.py:L45 (distance == 2.0)",
                "proximity_controller.py:L48 (hysteresis low/high band missing)"
            ],
            "risk_assessment": "CRITICAL_GAP"
        }
    return {
        "module": module_name,
        "line_coverage_pct": 91.0,
        "branch_coverage_pct": 88.0,
        "uncovered_boundary_branches": [],
        "risk_assessment": "ACCEPTABLE"
    }
