"""
Git & Cloud Storage Tools for AXIOM.
Handles source code inspection, AST syntax parsing, regression commit diffs,
and deterministic surgical patch generation for ENG.ai Master.
"""

import ast
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("axiom.tools.git")

# Synthetic Git Repository State for Golden Scenario
_SYNTHETIC_CODE = {
    "proximity_controller.py": '''"""
Passive Keyless Entry (PKE) Proximity Controller.
Evaluates key fob distance and determines vehicle lock state.
"""

class ProximityController:
    def __init__(self, unlock_threshold: float = 2.0):
        self.unlock_threshold = unlock_threshold
        self.is_unlocked = False

    def evaluate_distance(self, distance_meters: float) -> bool:
        # BUG: Single threshold condition without hysteresis deadband.
        # Causes rapid oscillation/chatter when distance fluctuates around 2.0m.
        if distance_meters <= self.unlock_threshold:
            self.is_unlocked = True
        else:
            self.is_unlocked = False
        return self.is_unlocked
'''
}

_REGRESSION_COMMIT = {
    "commit_sha": "7f2a1b49c0d",
    "author": "Dev Alpha <alpha@axiom.internal>",
    "date": "2026-10-02T14:22:10Z",
    "summary": "refactor: simplify proximity boundary check to single threshold",
    "changed_files": ["proximity_controller.py"],
    "diff": """--- a/proximity_controller.py
+++ b/proximity_controller.py
@@ -10,4 +10,4 @@
-        if not self.is_unlocked and distance_meters <= self.unlock_threshold - 0.2:
-            self.is_unlocked = True
-        elif self.is_unlocked and distance_meters >= self.unlock_threshold + 0.2:
-            self.is_unlocked = False
+        if distance_meters <= self.unlock_threshold:
+            self.is_unlocked = True
+        else:
+            self.is_unlocked = False
"""
}

_SURGICAL_PATCH = """--- a/proximity_controller.py
+++ b/proximity_controller.py
@@ -6,8 +6,12 @@
 class ProximityController:
-    def __init__(self, unlock_threshold: float = 2.0):
+    def __init__(self, unlock_threshold: float = 1.8, lock_threshold: float = 2.2):
         self.unlock_threshold = unlock_threshold
+        self.lock_threshold = lock_threshold
         self.is_unlocked = False

     def evaluate_distance(self, distance_meters: float) -> bool:
-        if distance_meters <= self.unlock_threshold:
+        # Hysteresis band prevents boundary hunting between 1.8m and 2.2m
+        if not self.is_unlocked and distance_meters <= self.unlock_threshold:
             self.is_unlocked = True
-        else:
+        elif self.is_unlocked and distance_meters >= self.lock_threshold:
             self.is_unlocked = False
         return self.is_unlocked
"""


def git_inspect_source_file(file_path: str = "proximity_controller.py") -> Dict[str, Any]:
    """Retrieves source code text from repository storage."""
    code = _SYNTHETIC_CODE.get(file_path, _SYNTHETIC_CODE["proximity_controller.py"])
    return {
        "file_path": file_path,
        "content": code,
        "line_count": len(code.splitlines())
    }


def git_get_commit_diff(target_file: str = "proximity_controller.py") -> Dict[str, Any]:
    """Returns the regression commit diff introducing the defect."""
    return _REGRESSION_COMMIT


def ast_analyze_code_structure(code_snippet: Optional[str] = None) -> Dict[str, Any]:
    """Parses Python source AST to isolate conditional thresholds and state mutators."""
    if not code_snippet:
        code_snippet = _SYNTHETIC_CODE["proximity_controller.py"]

    tree = ast.parse(code_snippet)
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test_src = ast.unparse(node.test)
            findings.append({
                "line": node.lineno,
                "type": "IfCondition",
                "condition": test_src,
                "has_hysteresis": "lock_threshold" in test_src or "hysteresis" in test_src or ("<=" in test_src and ">=" in test_src)
            })

    return {
        "ast_parsed": True,
        "conditional_nodes": findings,
        "root_cause_diagnosis": "Single-threshold condition detected at line 14: 'distance_meters <= self.unlock_threshold'. Lacks dual-threshold hysteresis band."
    }


def generate_surgical_patch(target_file: str = "proximity_controller.py") -> Dict[str, Any]:
    """Synthesizes the minimal verified hysteresis patch."""
    return {
        "target_file": target_file,
        "target_branch": "fix/gh-issue-107",
        "patch_diff": _SURGICAL_PATCH,
        "explanation": "Introduces dual-threshold hysteresis (unlock at <= 1.8m, lock at >= 2.2m) to prevent relay chatter around the 2.0m boundary."
    }


def validate_patch_syntax(patch_diff: str = _SURGICAL_PATCH) -> Dict[str, Any]:
    """Validates that the proposed patch produces valid, compilable Python syntax."""
    # Synthetic verification of patched code
    patched_code = '''
class ProximityController:
    def __init__(self, unlock_threshold: float = 1.8, lock_threshold: float = 2.2):
        self.unlock_threshold = unlock_threshold
        self.lock_threshold = lock_threshold
        self.is_unlocked = False

    def evaluate_distance(self, distance_meters: float) -> bool:
        if not self.is_unlocked and distance_meters <= self.unlock_threshold:
            self.is_unlocked = True
        elif self.is_unlocked and distance_meters >= self.lock_threshold:
            self.is_unlocked = False
        return self.is_unlocked
'''
    try:
        ast.parse(patched_code)
        return {
            "syntax_valid": True,
            "ast_compilation": "SUCCESS",
            "cyclomatic_complexity": 3,
            "security_lint_errors": 0
        }
    except Exception as e:
        return {
            "syntax_valid": False,
            "error": str(e)
        }
