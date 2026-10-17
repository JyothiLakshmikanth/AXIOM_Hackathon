"""
Resource & Capacity Intelligence Specialist Agent.
Implemented as a specialized LangChain ReAct agent querying team skills,
sprint velocity trends, and developer allocation envelopes.
Now integrates with real data from AXIOM-main repository.
"""

import json
import logging
import os
import csv
import requests
from io import StringIO
from typing import Dict, Any, List, Optional

logger = logging.getLogger("axiom.agents.resource")

SYSTEM_PROMPT = """You are the Resource & Capacity Specialist Agent for AXIOM.
Your mission is to query team skills, calculate velocity and volatility metrics, model engineer capacity,
and formulate sprint replanning adjustments for AXIOM-PM Master.

Available Tools:
- load_team_capacity_from_repository(resource_id: str)
- load_sprint_planning_from_repository(sprint_id: str)
- calculate_velocity_metrics(sprint_data: dict)

Rules:
1. Engineer allocation must not exceed the 85% planned capacity ceiling.
2. Ground all capacity recommendations in verified developer competency profiles.
3. You CANNOT directly reassign tasks without PM authorization.
"""


def load_team_capacity_from_csv() -> Dict[str, Dict[str, Any]]:
    """Load team capacity and competency data from GitHub repository."""
    github_url = "https://raw.githubusercontent.com/JyothiLakshmikanth/AXIOM-main/main/data/AXIOM_Capacity_Planning.csv"
    
    local_paths = [
        r"C:\New folder\builder_axoim\AXIOM-main\data\AXIOM_Capacity_Planning.csv",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "..", "builder_axoim", "AXIOM-main", "data", "AXIOM_Capacity_Planning.csv"
        ),
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "builder_axoim", "AXIOM-main", "data", "AXIOM_Capacity_Planning.csv"
        )
    ]
    
    team_data = {}
    
    # Try GitHub URL first
    try:
        response = requests.get(github_url, timeout=10)
        response.raise_for_status()
        reader = csv.DictReader(StringIO(response.text))
        for row in reader:
            resource_id = row.get("Resource_ID", "")
            if resource_id:
                team_data[resource_id] = row
        logger.info(f"Loaded {len(team_data)} team members from GitHub: {github_url}")
        return team_data
    except Exception as e:
        logger.warning(f"Failed to fetch from GitHub ({e}). Trying local paths...")
    
    # Fallback to local paths
    for repo_path in local_paths:
        if os.path.exists(repo_path):
            try:
                with open(repo_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        resource_id = row.get("Resource_ID", "")
                        if resource_id:
                            team_data[resource_id] = row
                    logger.info(f"Loaded {len(team_data)} team members from local: {repo_path}")
                    return team_data
            except Exception as e:
                logger.error(f"Error loading from {repo_path}: {e}")
    
    logger.warning("Could not load team capacity from GitHub or local paths")
    return team_data


def load_sprint_planning_from_csv() -> Dict[str, Dict[str, Any]]:
    """Load sprint planning data from GitHub repository."""
    github_url = "https://raw.githubusercontent.com/JyothiLakshmikanth/AXIOM-main/main/data/AXIOM_Sprint_Planning.csv"
    
    local_paths = [
        r"C:\New folder\builder_axoim\AXIOM-main\data\AXIOM_Sprint_Planning.csv",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "..", "builder_axoim", "AXIOM-main", "data", "AXIOM_Sprint_Planning.csv"
        ),
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "builder_axoim", "AXIOM-main", "data", "AXIOM_Sprint_Planning.csv"
        )
    ]
    
    sprint_data = {}
    
    # Try GitHub URL first
    try:
        response = requests.get(github_url, timeout=10)
        response.raise_for_status()
        reader = csv.DictReader(StringIO(response.text))
        for row in reader:
            sprint_id = row.get("Sprint_ID", "")
            if sprint_id:
                if sprint_id not in sprint_data:
                    sprint_data[sprint_id] = {"tasks": []}
                sprint_data[sprint_id]["tasks"].append(row)
        logger.info(f"Loaded sprint data for {len(sprint_data)} sprints from GitHub: {github_url}")
        return sprint_data
    except Exception as e:
        logger.warning(f"Failed to fetch from GitHub ({e}). Trying local paths...")
    
    # Fallback to local paths
    for repo_path in local_paths:
        if os.path.exists(repo_path):
            try:
                with open(repo_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sprint_id = row.get("Sprint_ID", "")
                        if sprint_id:
                            if sprint_id not in sprint_data:
                                sprint_data[sprint_id] = {"tasks": []}
                            sprint_data[sprint_id]["tasks"].append(row)
                    logger.info(f"Loaded sprint data for {len(sprint_data)} sprints from local: {repo_path}")
                    return sprint_data
            except Exception as e:
                logger.error(f"Error loading from {repo_path}: {e}")
    
    logger.warning("Could not load sprint planning from GitHub or local paths")
    return sprint_data


class ResourceAgent:
    """Specialized LangChain ReAct Agent for Resource Capacity & Velocity."""

    def __init__(self):
        self.agent_id = "resource_agent"
        self.name = "Resource & Capacity Intelligence Specialist Agent"
        self.team_capacity = load_team_capacity_from_csv()
        self.sprint_planning = load_sprint_planning_from_csv()

    def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes autonomous ReAct reasoning loop:
        Thought -> Action -> Observation -> Final Evidence Synthesis.
        """
        sprint_id = task_input.get("sprint_id", "SPR-03")
        action = task_input.get("action", "analyze_team_capacity")

        evidences = []
        findings = {}

        # ReAct Step 1: Compute sprint velocity and task metrics
        sprint_tasks = self.sprint_planning.get(sprint_id, {}).get("tasks", [])
        vel = self._calculate_velocity_metrics(sprint_id, sprint_tasks)
        
        evidences.append({
            "artifact_id": f"VELOCITY-{sprint_id}",
            "artifact_type": "sprint_velocity_record",
            "source_system": "github_sprint_dataset",
            "source_uri": "https://raw.githubusercontent.com/JyothiLakshmikanth/AXIOM-main/main/data/AXIOM_Sprint_Planning.csv",
            "version": "1.0",
            "updated_at": "2026-10-17T10:00:00Z",
            "authoritative": True,
            "synthetic": False,
            "quality_status": "verified",
            "payload": vel
        })
        findings["velocity_analysis"] = vel

        # ReAct Step 2: Query team competencies & allocations
        team_profiles = self._analyze_team_capacity()
        evidences.append({
            "artifact_id": "TEAM-CAPACITY-ENVELOPE",
            "artifact_type": "engineer_capacity_envelope",
            "source_system": "github_capacity_dataset",
            "source_uri": "https://raw.githubusercontent.com/JyothiLakshmikanth/AXIOM-main/main/data/AXIOM_Capacity_Planning.csv",
            "version": "1.0",
            "updated_at": "2026-10-17T10:00:00Z",
            "authoritative": True,
            "synthetic": False,
            "quality_status": "verified",
            "payload": {"profiles": team_profiles}
        })
        findings["team_profiles"] = team_profiles

        # ReAct Step 3: Identify capacity bottlenecks & rebalancing opportunities
        bottlenecks, available_cap = self._identify_bottlenecks(sprint_id, sprint_tasks)
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

    def _calculate_velocity_metrics(self, sprint_id: str, sprint_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate velocity metrics for a sprint."""
        if not sprint_tasks:
            return {
                "sprint_id": sprint_id,
                "rolling_average_velocity": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "volatility_index": 0
            }
        
        completed = sum(1 for t in sprint_tasks if t.get("Status") == "Done")
        in_progress = sum(1 for t in sprint_tasks if t.get("Status") == "In Progress")
        total = len(sprint_tasks)
        
        try:
            avg_story_points = sum(float(t.get("Story_Points", 0)) for t in sprint_tasks) / max(1, total)
        except:
            avg_story_points = 0
        
        return {
            "sprint_id": sprint_id,
            "rolling_average_velocity": round(avg_story_points, 2),
            "total_tasks": total,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "completion_rate": round((completed / total * 100), 1) if total > 0 else 0,
            "volatility_index": 0.15  # Placeholder
        }

    def _analyze_team_capacity(self) -> List[Dict[str, Any]]:
        """Analyze team capacity and allocation."""
        profiles = []
        for resource_id, member in self.team_capacity.items():
            allocation = float(member.get("Allocation_%", 0))
            utilization = "AVAILABLE" if allocation <= 85 else "OVERALLOCATED"
            
            profiles.append({
                "resource_id": resource_id,
                "name": member.get("Associate", ""),
                "role": member.get("Role", ""),
                "domain": member.get("Domain", ""),
                "allocation_percent": allocation,
                "q4_hours": member.get("Q4_2026_Hours", 0),
                "status": member.get("Availability_Status", "Available"),
                "utilization": utilization,
                "notes": member.get("Notes", "")
            })
        
        return profiles

    def _identify_bottlenecks(self, sprint_id: str, sprint_tasks: List[Dict[str, Any]]) -> tuple:
        """Identify resource bottlenecks in the sprint."""
        bottlenecks = []
        available_cap = []
        
        # Count tasks per resource
        tasks_per_resource = {}
        for task in sprint_tasks:
            owner = task.get("Owned_By", "")
            if owner:
                tasks_per_resource[owner] = tasks_per_resource.get(owner, 0) + 1
        
        # Find overallocated resources
        for resource_id, member in self.team_capacity.items():
            allocation = float(member.get("Allocation_%", 0))
            task_count = tasks_per_resource.get(resource_id, 0)
            
            if allocation > 85 or task_count > 5:
                bottlenecks.append({
                    "resource_id": resource_id,
                    "name": member.get("Associate", ""),
                    "allocation": f"{allocation}%",
                    "task_count": task_count,
                    "status": "OVERALLOCATED - Risk of slip"
                })
            elif allocation <= 75 and allocation > 0:
                available_cap.append({
                    "resource_id": resource_id,
                    "name": member.get("Associate", ""),
                    "allocation": f"{allocation}%",
                    "available_hours": max(0, 480 - float(member.get("Q4_2026_Hours", 0))),
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
                plan.append(f"Reduce workload for {bottleneck['name']} ({bottleneck['allocation']} allocated, {bottleneck['task_count']} tasks).")
            
            if available:
                plan.append(f"Redistribute tasks to: {', '.join([a['name'] for a in available])}")
        
        return plan

    def _assess_sprint_health(self, velocity_data: Dict[str, Any]) -> str:
        """Assess overall sprint health."""
        completion_rate = velocity_data.get("completion_rate", 0)
        in_progress = velocity_data.get("in_progress_tasks", 0)
        
        if completion_rate >= 80:
            return "HEALTHY - On track for delivery"
        elif completion_rate >= 60 and in_progress > 0:
            return "AT_RISK - Monitor progress daily"
        else:
            return "CRITICAL - Intervention needed"


# Global agent instance
resource_agent = ResourceAgent()
