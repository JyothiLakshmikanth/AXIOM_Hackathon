"""
Test Generation & Coverage Tool for AXIOM Test Agent.
Evaluates test coverage for requirements and descriptions, identifies gaps,
and synthesizes new ISO 29119 test specifications and pytest reproduction suites.
"""

import re
import json
import logging
from typing import Union, Dict, Any, List

logger = logging.getLogger("axiom.agents.tools.test_generation")

try:
    from langchain_core.tools import tool
except ImportError:
    try:
        from langchain.tools import tool
    except ImportError:
        def tool(func):
            func.name = func.__name__
            func.description = func.__doc__
            func.run = lambda *args, **kwargs: func(*args, **kwargs)
            return func

from agents.utils.test_utils import evaluate_and_generate_test_cases, fetch_test_cases


@tool
def test_generation_tool(query_input: Union[dict, str]) -> str:
    """
    Evaluates test coverage for requirement IDs or feature/defect descriptions.
    Determines if new test cases are needed for better coverage (boundary, negative, variant, or edge-case),
    and synthesizes new test cases along with executable pytest suites.
    Input can be a JSON object or string with:
    - 'requirement_ids': list of Requirement IDs
    - 'description': description of defect, feature, or scenario
    - 'existing_test_ids': optional list of currently linked test case IDs
    Returns: JSON with coverage gap analysis, new_test_cases_needed flag, and synthesized test cases.
    """
    try:
        requirement_ids: List[str] = []
        description: str = ""
        existing_tests: List[Dict[str, Any]] = []

        if isinstance(query_input, dict):
            if "requirement_ids" in query_input:
                val = query_input["requirement_ids"]
                requirement_ids = val if isinstance(val, list) else [val]
            elif "requirement_id" in query_input:
                requirement_ids = [query_input["requirement_id"]]

            description = query_input.get("description") or query_input.get("defect_summary") or query_input.get("query") or ""
            
            # If caller passed existing test IDs, fetch them
            existing_ids = query_input.get("existing_test_ids") or []
            if existing_ids:
                existing_tests = fetch_test_cases(test_case_ids=existing_ids)
            elif requirement_ids:
                existing_tests = fetch_test_cases(requirement_ids=requirement_ids)

        elif isinstance(query_input, str):
            try:
                parsed = json.loads(query_input)
                if isinstance(parsed, dict):
                    return test_generation_tool.run(parsed)
            except Exception:
                pass

            reqs = re.findall(r"REQ-[A-Za-z0-9\-]+", query_input, re.IGNORECASE)
            requirement_ids.extend(reqs)
            description = query_input.strip()
            if requirement_ids:
                existing_tests = fetch_test_cases(requirement_ids=requirement_ids)

        # Run evaluation and generation engine
        result = evaluate_and_generate_test_cases(
            requirement_ids=requirement_ids,
            descriptions=description,
            existing_tests=existing_tests
        )

        return json.dumps({
            "source": "axiom_test_generation_engine",
            "evaluated_requirements": requirement_ids,
            "evaluated_scenario": description,
            "coverage_assessment": {
                "status": result.get("coverage_status"),
                "total_existing_linked_tests": result.get("total_existing_tests"),
                "coverage_gaps_identified": result.get("coverage_gaps", []),
                "coverage_score": result.get("coverage_score")
            },
            "new_test_cases_needed": result.get("new_test_cases_needed", False),
            "generated_test_cases": result.get("generated_test_cases", []),
            "synthesized_pytest_code": result.get("synthesized_pytest_code", "")
        })

    except Exception as e:
        logger.error(f"Error in test_generation_tool: {e}", exc_info=True)
        return json.dumps({"error": f"Tool execution failed: {str(e)}", "new_test_cases_needed": False, "generated_test_cases": []})
