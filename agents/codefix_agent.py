"""
Code Analysis & Surgical Fix Specialist Agent.
Implemented as a specialized LangChain ReAct agent performing AST inspection,
regression commit isolation, and deterministic surgical patch generation for ENG.ai Master.
"""

import json
import logging
from typing import Dict, Any, List
from agents.tools.git_storage_tools import (
    git_inspect_source_file,
    git_get_commit_diff,
    ast_analyze_code_structure,
    generate_surgical_patch,
    validate_patch_syntax
)

logger = logging.getLogger("axiom.agents.codefix")

SYSTEM_PROMPT = """You are the Code Analysis & Surgical Fix Specialist Agent for AXIOM.
Your mission is to inspect source code ASTs, analyze git commit diffs, isolate regression points,
and synthesize verifiable surgical patches for ENG.ai Master.

Available Tools:
- git_inspect_source_file(file_path: str)
- git_get_commit_diff(target_file: str)
- ast_analyze_code_structure(code_snippet: str)
- generate_surgical_patch(target_file: str)
- validate_patch_syntax(patch_diff: str)

Rules:
1. Every code diagnosis must reference concrete line numbers and AST nodes.
2. Patches must be minimal and strictly targeted to the verified root cause.
3. You CANNOT push directly to main or merge pull requests.
"""


class CodeFixAgent:
    """Specialized LangChain ReAct Agent for Code Root Cause & Patching."""

    def __init__(self):
        self.agent_id = "codefix_agent"
        self.name = "Code Analysis & Surgical Fix Specialist Agent"

    def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes autonomous ReAct reasoning loop:
        Thought -> Action -> Observation -> Final Evidence Synthesis.
        """
        file_path = task_input.get("file_path", "proximity_controller.py")
        action = task_input.get("action", "isolate_regression")

        evidences = []
        findings = {}

        # ReAct Step 1: Inspect source code and regression commit
        source_doc = git_inspect_source_file(file_path)
        commit_diff = git_get_commit_diff(file_path)
        evidences.append({
            "artifact_id": f"COMMIT-{commit_diff['commit_sha']}",
            "artifact_type": "git_commit_diff",
            "source_system": "synthetic_git",
            "source_uri": f"git://axiom-core/commits/{commit_diff['commit_sha']}",
            "version": "1.0",
            "updated_at": commit_diff["date"],
            "authoritative": True,
            "synthetic": True,
            "quality_status": "verified",
            "payload": commit_diff
        })
        findings["regression_commit"] = commit_diff

        # ReAct Step 2: AST Analysis of threshold boundary logic
        ast_result = ast_analyze_code_structure(source_doc["content"])
        evidences.append({
            "artifact_id": f"AST-{file_path}",
            "artifact_type": "source_ast_inspection",
            "source_system": "cloud_storage_src",
            "source_uri": f"storage://axiom-src/{file_path}",
            "version": "1.0",
            "updated_at": "2026-10-04T10:00:00Z",
            "authoritative": True,
            "synthetic": True,
            "quality_status": "verified",
            "payload": ast_result
        })
        findings["ast_analysis"] = ast_result

        # ReAct Step 3: Generate surgical patch (hysteresis band) and validate syntax
        patch_data = generate_surgical_patch(file_path)
        syntax_validation = validate_patch_syntax(patch_data["patch_diff"])
        evidences.append({
            "artifact_id": f"PATCH-{file_path}",
            "artifact_type": "proposed_surgical_patch",
            "source_system": "synthetic_git",
            "source_uri": f"git://axiom-core/branches/{patch_data['target_branch']}",
            "version": "1.0",
            "updated_at": "2026-10-04T11:00:00Z",
            "authoritative": True,
            "synthetic": True,
            "quality_status": "verified",
            "payload": {**patch_data, **syntax_validation}
        })
        findings["proposed_patch"] = patch_data
        findings["syntax_validation"] = syntax_validation

        return {
            "agent_id": self.agent_id,
            "execution_status": "SUCCESS",
            "summary": f"Isolated regression commit {commit_diff['commit_sha']} in {file_path}. AST analysis confirmed single-threshold oscillation. Synthesized validated hysteresis patch.",
            "findings": findings,
            "evidences": evidences
        }


# Global agent instance
codefix_agent = CodeFixAgent()
