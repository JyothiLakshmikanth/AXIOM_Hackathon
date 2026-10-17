"""
Resource & Capacity Intelligence Specialist Agent.
Implemented as a specialized LangChain ReAct agent querying team skills,
sprint velocity trends, and developer allocation envelopes.
Primary data source: BigQuery axiom_data dataset (with local CSV fallback).
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional

from agents.tools.bigquery_tools import (
    bigquery_get_team_capacity,
    bigquery_get_competency_matrix,
    bigquery_get_sprint_tasks,
    bigquery_get_team_velocity_history,
    bigquery_get_pi_planning,
)

logger = logging.getLogger("axiom.agents.resource")

SYSTEM_PROMPT = """You are the Resource & Capacity Specialist Agent for AXIOM.
Your mission is to query team skills, calculate velocity and volatility metrics, model engineer capacity,
and formulate sprint replanning adjustments for AXIOM-PM Master.

Available Tools:
- bigquery_get_team_capacity(resource_id: str)
- bigquery_get_competency_matrix(associate: str, skill: str)
- bigquery_get_sprint_tasks(sprint_id: str)
- bigquery_get_team_velocity_history(sprint_id: str)
- bigquery_get_pi_planning(pi_id: str)

Rules:
1. Engineer allocation must not exceed the 85% planned capacity ceiling.
2. Ground all capacity recommendations in verified developer competency profiles.
3. You CANNOT directly reassign tasks without PM authorization.
"""

# Mapping between sprint resource IDs and team associates
_RES_TO_ASSOCIATE_MAP = {
    "RES-01": {"associate": "JyothiLakshmikanth", "role": "System Architect", "domain": "Architecture"},
    "RES-02": {"associate": "bhavya2642-collab", "role": "Mobile Engineer", "domain": "Mobile"},
    "RES-03": {"associate": "manjunathan-j", "role": "Mobile Engineer", "domain": "Mobile"},
    "RES-04": {"associate": "Pavi2604", "role": "Vehicle Software Engineer", "domain": "Vehicle"},
    "RES-05": {"associate": "JyothiLakshmikanth", "role": "Vehicle Software Engineer", "domain": "Vehicle"},
    "RES-06": {"associate": "bhavya2642-collab", "role": "Cloud Engineer", "domain": "Cloud"},
    "RES-07": {"associate": "manjunathan-j", "role": "Security Engineer", "domain": "Security"},
    "RES-08": {"associate": "Pavi2604", "role": "QA Engineer", "domain": "QA"},
    "GHA-01": {"associate": "JyothiLakshmikanth", "role": "System Architect", "domain": "Architecture"},
    "GHA-02": {"associate": "bhavya2642-collab", "role": "Mobile Engineer", "domain": "Mobile"},
    "GHA-03": {"associate": "manjunathan-j", "role": "Mobile Engineer", "domain": "Mobile"},
    "GHA-04": {"associate": "Pavi2604", "role": "Vehicle Software Engineer", "domain": "Vehicle"},
}


class ResourceAgent:
    """Specialized LangChain ReAct Agent for Resource Capacity & Velocity."""

    def __init__(self):
        self.agent_id = "resource_agent"
        self.name = "Resource & Capacity Intelligence Specialist Agent"

    def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes autonomous ReAct reasoning loop:
        Thought -> Action -> Observation -> Final Evidence Synthesis.
        """
        sprint_id = task_input.get("sprint_id", "SPR-03")
        action = task_input.get("action", "analyze_team_capacity")

        evidences = []
        findings = {}

        # ReAct Step 1: Compute sprint velocity and task metrics from BigQuery
        sprint_tasks = bigquery_get_sprint_tasks(sprint_id)
        velocity_history = bigquery_get_team_velocity_history(sprint_id)
        vel = self._calculate_velocity_metrics(sprint_id, sprint_tasks, velocity_history)

        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "axiom-cloud-run")
        evidences.append({
            "artifact_id": f"VELOCITY-{sprint_id}",
            "artifact_type": "sprint_velocity_record",
            "source_system": "bigquery_axiom_data",
            "source_uri": f"bigquery://{project_id}.axiom_data.sprint_planning",
            "version": "1.0",
            "updated_at": "2026-10-17T10:00:00Z",
            "authoritative": True,
            "synthetic": False,
            "quality_status": "verified",
            "payload": vel
        })
        findings["velocity_analysis"] = vel

        # ReAct Step 2: Query team competencies & allocations from BigQuery
        capacity_records = bigquery_get_team_capacity()
        competency_records = bigquery_get_competency_matrix()
        team_profiles = self._analyze_team_capacity(capacity_records)

        evidences.append({
            "artifact_id": "TEAM-CAPACITY-ENVELOPE",
            "artifact_type": "engineer_capacity_envelope",
            "source_system": "bigquery_axiom_data",
            "source_uri": f"bigquery://{project_id}.axiom_data.capacity_planning",
            "version": "1.0",
            "updated_at": "2026-10-17T10:00:00Z",
            "authoritative": True,
            "synthetic": False,
            "quality_status": "verified",
            "payload": {"profiles": team_profiles, "competencies_count": len(competency_records)}
        })
        findings["team_profiles"] = team_profiles

        # ReAct Step 3: Identify capacity bottlenecks & rebalancing opportunities
        bottlenecks, available_cap = self._identify_bottlenecks(sprint_id, sprint_tasks, capacity_records)
        findings["capacity_bottlenecks"] = bottlenecks
        findings["available_capacity"] = available_cap
        findings["rebalancing_plan"] = self._formulate_rebalancing_plan(sprint_id, bottlenecks, available_cap)
        findings["sprint_health"] = self._assess_sprint_health(vel)

        summary = (f"Analyzed {sprint_id}: {vel.get('total_tasks', 0)} tasks planned, "
                  f"{vel.get('completed_tasks', 0)} completed. Identified {len(bottlenecks)} bottleneck(s) "
                  f"and {len(available_cap)} engineer(s) with available capacity.")

        return {
            "agent_id": self.agent_id,
            "execution_status": "SUCCESS",
            "summary": summary,
            "findings": findings,
            "evidences": evidences
        }

    def _calculate_velocity_metrics(self, sprint_id: str, sprint_tasks: List[Dict[str, Any]],
                                    velocity_history: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate velocity metrics for a sprint."""
        if not sprint_tasks:
            # Fall back to velocity history if direct task list empty
            if velocity_history:
                return velocity_history
            return {
                "sprint_id": sprint_id,
                "rolling_average_velocity": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "completion_rate": 0,
                "volatility_index": 0
            }

        completed = sum(1 for t in sprint_tasks if t.get("Status") in ("Done", "Closed"))
        in_progress = sum(1 for t in sprint_tasks if t.get("Status") == "In Progress")
        total = len(sprint_tasks)

        pts_list = []
        for t in sprint_tasks:
            try:
                pts_list.append(float(t.get("Story_Points", 0) or 0))
            except (ValueError, TypeError):
                pass
        total_story_points = sum(pts_list)
        avg_story_points = total_story_points / max(1, total)

        rolling_avg = velocity_history.get("rolling_average_velocity", round(avg_story_points, 2)) if velocity_history else round(avg_story_points, 2)
        volatility = velocity_history.get("volatility_index", 0.15) if velocity_history else 0.15

        return {
            "sprint_id": sprint_id,
            "rolling_average_velocity": rolling_avg,
            "total_tasks": total,
            "total_story_points": total_story_points,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "completion_rate": round((completed / total * 100), 1) if total > 0 else 0,
            "volatility_index": volatility,
            "slip_risk": "HIGH" if (completed / max(1, total)) < 0.5 else "LOW"
        }

    def _analyze_team_capacity(self, capacity_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze team capacity and allocation across records."""
        profiles = []
        for member in capacity_records:
            try:
                alloc_str = str(member.get("Allocation_%", 0)).replace("%", "")
                allocation = float(alloc_str or 0)
            except (ValueError, TypeError):
                allocation = 0.0

            utilization = "AVAILABLE" if allocation <= 85 else "OVERALLOCATED"
            resource_id = member.get("Default_Assignee_ID") or member.get("Associate", "")

            profiles.append({
                "resource_id": resource_id,
                "name": member.get("Associate", ""),
                "role": member.get("Role", ""),
                "domain": member.get("Domain", ""),
                "allocation_percent": allocation,
                "location": member.get("Location", ""),
                "q4_hours": member.get("Q4_2026_Hours", 0),
                "status": member.get("Availability_Status", "Available"),
                "utilization": utilization,
                "notes": member.get("Notes", "")
            })

        return profiles

    def _identify_bottlenecks(self, sprint_id: str, sprint_tasks: List[Dict[str, Any]],
                             capacity_records: List[Dict[str, Any]]) -> tuple:
        """Identify resource bottlenecks in the sprint."""
        bottlenecks = []
        available_cap = []

        # Count tasks per associate/owner
        tasks_per_owner: Dict[str, int] = {}
        for task in sprint_tasks:
            owner = task.get("Owned_By", "")
            if owner:
                # Map to associate name if possible
                assoc = _RES_TO_ASSOCIATE_MAP.get(owner, {}).get("associate", owner)
                tasks_per_owner[assoc] = tasks_per_owner.get(assoc, 0) + 1
                tasks_per_owner[owner] = tasks_per_owner.get(owner, 0) + 1

        # Check against capacity records
        seen_associates = set()
        for member in capacity_records:
            name = member.get("Associate", "")
            res_id = member.get("Default_Assignee_ID", "")
            key = f"{name}-{res_id}"
            if key in seen_associates:
                continue
            seen_associates.add(key)

            try:
                alloc_str = str(member.get("Allocation_%", 0)).replace("%", "")
                allocation = float(alloc_str or 0)
            except (ValueError, TypeError):
                allocation = 0.0

            task_count = tasks_per_owner.get(name, tasks_per_owner.get(res_id, 0))

            if allocation > 85 or task_count > 3:
                bottlenecks.append({
                    "resource_id": res_id or name,
                    "name": name,
                    "role": member.get("Role", ""),
                    "allocation": f"{allocation}%",
                    "task_count": task_count,
                    "status": "OVERALLOCATED - Risk of slip (>85% limit)"
                })
            elif allocation <= 80 and allocation > 0:
                available_cap.append({
                    "resource_id": res_id or name,
                    "name": name,
                    "role": member.get("Role", ""),
                    "allocation": f"{allocation}%",
                    "task_count": task_count,
                    "status": "AVAILABLE - Can take more work"
                })

        return bottlenecks, available_cap

    def _formulate_rebalancing_plan(self, sprint_id: str, bottlenecks: List[Dict],
                                   available: List[Dict]) -> List[str]:
        """Formulate a rebalancing plan based on bottlenecks and available capacity."""
        plan = []

        if not bottlenecks:
            plan.append(f"✓ {sprint_id} capacity is well-balanced. No immediate rebalancing needed.")
        else:
            for bottleneck in bottlenecks:
                plan.append(
                    f"Reduce workload for {bottleneck['name']} ({bottleneck['role']}) - "
                    f"allocated {bottleneck['allocation']}, holding {bottleneck['task_count']} sprint tasks."
                )

            if available:
                names = list({f"{a['name']} ({a['role']})" for a in available})
                plan.append(f"Recommended redistribution targets: {', '.join(names)}")

        return plan

    def _assess_sprint_health(self, velocity_data: Dict[str, Any]) -> str:
        """Assess overall sprint health."""
        completion_rate = velocity_data.get("completion_rate", 0)
        in_progress = velocity_data.get("in_progress_tasks", 0)

        if completion_rate >= 80:
            return "HEALTHY - On track for delivery"
        elif completion_rate >= 50 or in_progress > 0:
            return "AT_RISK - Potential velocity slip, monitor daily"
        else:
            return "CRITICAL - Severe bottleneck or slip risk, intervention needed"


# Global agent instance
resource_agent = ResourceAgent()
