"""
Requirement Details Tool for AXIOM Requirement Agent.
Implements the LangChain Tool for retrieving full specification details
of single or multiple requirements from Neo4j Knowledge Graph.
"""

import re
import json
import logging
from typing import Union, Dict, Any, List

logger = logging.getLogger("axiom.agents.tools.requirement_details")

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

from agents.utils.neo4j_utils import get_requirement_details


@tool
def requirement_details_tool(query_input: Union[dict, list, str]) -> str:
    """
    Fetches full specification details for single or multiple Requirement IDs from Neo4j.
    Input can be:
    - A list of requirement IDs (e.g., ['REQ-L2-001', 'REQ-L3-001'])
    - A JSON object with 'requirement_ids' (list) or 'requirement_id' (string)
    - A comma-separated string or query containing requirement IDs
    Returns full primary text, level, status, verification criteria, variants, component, and linked test cases.
    """
    try:
        requirement_ids = []

        if isinstance(query_input, list):
            requirement_ids = query_input
        elif isinstance(query_input, dict):
            if "requirement_ids" in query_input:
                requirement_ids = query_input["requirement_ids"]
            elif "requirement_id" in query_input:
                requirement_ids = [query_input["requirement_id"]]
        elif isinstance(query_input, str):
            try:
                parsed = json.loads(query_input)
                if isinstance(parsed, list):
                    requirement_ids = parsed
                elif isinstance(parsed, dict):
                    requirement_ids = parsed.get("requirement_ids") or [parsed.get("requirement_id")]
            except Exception:
                # Extract REQ- tokens using regex
                matches = re.findall(r"REQ-[A-Za-z0-9\-]+", query_input, re.IGNORECASE)
                if matches:
                    requirement_ids = matches
                else:
                    requirement_ids = [query_input.strip()]

        # Clean list
        clean_ids = [str(r).strip() for r in requirement_ids if str(r).strip() and str(r).strip() != "None"]

        if not clean_ids:
            return json.dumps({
                "source": "neo4j_requirement_store",
                "error": "No valid Requirement IDs provided.",
                "total_found": 0,
                "requirements": [],
                "confidence": 0.0
            })

        details = get_requirement_details(clean_ids)

        return json.dumps({
            "source": "neo4j_requirement_store",
            "search_type": "requirement_details_lookup",
            "requested_ids": clean_ids,
            "total_found": len(details),
            "requirements": details,
            "confidence": 0.95 if details else 0.0
        })

    except Exception as e:
        logger.error(f"Error executing requirement_details_tool: {e}", exc_info=True)
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})
