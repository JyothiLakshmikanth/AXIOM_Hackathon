"""
Test Details Fetcher Tool for AXIOM Test Agent.
Retrieves full test case specifications (single or multiple) using:
1. Test Case IDs (e.g. TC-ENR-001, TC-UNL-006)
2. Requirement IDs (e.g. REQ-L2-001, REQ-L5-005)
3. Semantic embedding search on free-form descriptions/defect summaries.
"""

import re
import json
import logging
from typing import Union, Dict, Any, List

logger = logging.getLogger("axiom.agents.tools.test_fetcher")

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

from agents.utils.test_utils import fetch_test_cases


@tool
def test_details_tool(query_input: Union[dict, list, str]) -> str:
    """
    Fetches full test case specifications from the Master Test Store.
    Input can be:
    - A dictionary: {'test_case_ids': [...], 'requirement_ids': [...], 'description': '...'}
    - A list of test case IDs or requirement IDs
    - A free-form string containing Test Case IDs (TC-...), Requirement IDs (REQ-...), or a description.
    Returns: JSON containing matching test cases with full fields (steps, objective, expected result, priority, status, variants).
    """
    try:
        test_case_ids: List[str] = []
        requirement_ids: List[str] = []
        description: str = ""

        if isinstance(query_input, dict):
            if "test_case_ids" in query_input:
                val = query_input["test_case_ids"]
                test_case_ids = val if isinstance(val, list) else [val]
            elif "test_case_id" in query_input:
                test_case_ids = [query_input["test_case_id"]]

            if "requirement_ids" in query_input:
                val = query_input["requirement_ids"]
                requirement_ids = val if isinstance(val, list) else [val]
            elif "requirement_id" in query_input:
                requirement_ids = [query_input["requirement_id"]]

            description = query_input.get("description") or query_input.get("query") or ""

        elif isinstance(query_input, list):
            for item in query_input:
                s = str(item).strip()
                if s.upper().startswith("TC-"):
                    test_case_ids.append(s)
                elif s.upper().startswith("REQ-"):
                    requirement_ids.append(s)
                else:
                    description += f" {s}"

        elif isinstance(query_input, str):
            try:
                parsed = json.loads(query_input)
                if isinstance(parsed, dict):
                    return test_details_tool.run(parsed)
                elif isinstance(parsed, list):
                    return test_details_tool.run(parsed)
            except Exception:
                pass

            # Extract TC-... and REQ-... tokens using regex
            tcs = re.findall(r"TC-[A-Za-z0-9\-]+", query_input, re.IGNORECASE)
            reqs = re.findall(r"REQ-[A-Za-z0-9\-]+", query_input, re.IGNORECASE)
            test_case_ids.extend(tcs)
            requirement_ids.extend(reqs)

            # If no explicit IDs found, treat the entire string as a description query
            if not tcs and not reqs:
                description = query_input.strip()
            else:
                # Retain residual text as description if meaningful
                cleaned = re.sub(r"(TC|REQ)-[A-Za-z0-9\-]+", "", query_input, flags=re.IGNORECASE).strip()
                if len(cleaned) > 10:
                    description = cleaned

        # Query the underlying store
        results = fetch_test_cases(
            test_case_ids=test_case_ids,
            requirement_ids=requirement_ids,
            description=description,
            top_k=5
        )

        return json.dumps({
            "source": "test_cases_master_store",
            "search_criteria": {
                "test_case_ids": test_case_ids,
                "requirement_ids": requirement_ids,
                "description": description
            },
            "total_retrieved": len(results),
            "test_cases": results,
            "confidence": 0.95 if results else 0.0
        })

    except Exception as e:
        logger.error(f"Error in test_details_tool: {e}", exc_info=True)
        return json.dumps({"error": f"Tool execution failed: {str(e)}", "total_retrieved": 0, "test_cases": []})
