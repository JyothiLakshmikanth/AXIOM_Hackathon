"""
Impact Analysis Tool for AXIOM Requirement Agent.
Implements the single LangChain Tool routing between Direct ID Graph Traversal and Vector Embedding Search.
"""

import json
import logging
from typing import Union, Dict, Any

logger = logging.getLogger("axiom.agents.tools.impact_analysis")

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

from agents.utils.neo4j_utils import get_impact_by_ids, vector_search_requirements


@tool
def impact_analysis_tool(query_input: Union[dict, str]) -> str:
    """
    Analyzes the impact and dependencies of requirements. 
    Input must be a JSON object or string with either 'requirement_ids' (list of strings) 
    OR 'defect_description' (string) for vector search.
    """
    try:
        # Parse input if it's a string, otherwise use as dict
        if isinstance(query_input, str):
            try:
                query_input = json.loads(query_input)
            except Exception:
                # If plain string passed, treat as defect_description or comma-separated req IDs
                if "REQ-" in query_input.upper():
                    import re
                    ids = re.findall(r"REQ-[A-Za-z0-9\-]+", query_input, re.IGNORECASE)
                    query_input = {"requirement_ids": ids}
                else:
                    query_input = {"defect_description": query_input}

        requirement_ids = query_input.get("requirement_ids", [])
        defect_description = query_input.get("defect_description", "")

        # Normalize requirement_ids if single string passed
        if isinstance(requirement_ids, str):
            requirement_ids = [requirement_ids]

        # PATH 1: Requirement IDs are provided
        if requirement_ids and len(requirement_ids) > 0:
            impact_data = get_impact_by_ids(requirement_ids)
            return json.dumps({
                "source": "neo4j_graph_traversal",
                "search_type": "direct_id_lookup",
                "target_ids": requirement_ids,
                "data": impact_data,
                "total_impacted_records": len(impact_data),
                "confidence": 0.95
            })

        # PATH 2: No IDs provided, use Vector Search on defect description
        elif defect_description:
            matched_reqs = vector_search_requirements(defect_description, top_k=3)
            matched_ids = [req["requirement_id"] for req in matched_reqs]

            if matched_ids:
                impact_data = get_impact_by_ids(matched_ids)
                return json.dumps({
                    "source": "neo4j_vector_search",
                    "search_type": "semantic_vector_lookup",
                    "query_text": defect_description,
                    "matched_requirements": matched_reqs,
                    "impact_data": impact_data,
                    "confidence": 0.85
                })
            else:
                return json.dumps({
                    "source": "neo4j",
                    "error": "No relevant requirements found for the provided defect description.",
                    "confidence": 0.0
                })

        else:
            return json.dumps({
                "error": "Invalid input. Provide either 'requirement_ids' (list) or 'defect_description' (string)."
            })

    except Exception as e:
        logger.error(f"Error executing impact_analysis_tool: {e}", exc_info=True)
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})
