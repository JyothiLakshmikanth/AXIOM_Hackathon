"""
AXIOM: Google Cloud Platform Cloud Run Web Application & API Server.
Exposes REST endpoints for the LangGraph multi-agent cognitive architecture
and serves the Visual-First Chat Interface.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure stdout handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from orchestrator.graph import run_axiom_orchestration
from agents.tools.neo4j_tools import _DYNAMIC_KG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("axiom.app")

app = FastAPI(
    title="AXIOM Multi-Agent Intelligence System",
    description="Google Cloud-deployed Evidence-Driven Multi-Agent System with PM.ai & ENG.ai Masters.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default-session"


@app.get("/api/health")
def healthcheck():
    """GCP Cloud Run Health Check Probe."""
    return {
        "status": "healthy",
        "service": "axiom-orchestrator",
        "cloud_provider": "Google Cloud Platform",
        "runtime": "Cloud Run / Python 3.12",
        "masters": ["PM.ai", "ENG.ai"],
        "knowledge_graph_nodes": len(_DYNAMIC_KG.nodes),
        "knowledge_graph_edges": len(_DYNAMIC_KG.edges)
    }


@app.get("/api/kg/stats")
def get_kg_stats():
    """Returns real-time statistics of the Neo4j Knowledge Graph."""
    node_labels = {}
    for node in _DYNAMIC_KG.nodes.values():
        lbl = node.get("label", "Unknown")
        node_labels[lbl] = node_labels.get(lbl, 0) + 1

    edge_types = {}
    for edge in _DYNAMIC_KG.edges:
        rel = edge.get("rel", "RELATED_TO")
        edge_types[rel] = edge_types.get(rel, 0) + 1

    return {
        "total_nodes": len(_DYNAMIC_KG.nodes),
        "total_edges": len(_DYNAMIC_KG.edges),
        "node_breakdown": node_labels,
        "edge_breakdown": edge_types,
        "direct_edges_count": sum(1 for e in _DYNAMIC_KG.edges if e.get("category") == "direct"),
        "semantic_edges_count": sum(1 for e in _DYNAMIC_KG.edges if e.get("category") == "semantic")
    }


@app.post("/api/chat")
def handle_chat(payload: ChatRequest):
    """
    Main Orchestration Endpoint:
    Executes top-level intent router, PM.ai / ENG.ai cognitive master loops,
    and visual-first image generation.
    """
    query = payload.query.strip()
    if not query:
        return JSONResponse(status_code=400, content={"error": "Empty query."})

    logger.info(f"Incoming Chat Query: '{query}'")
    try:
        result = run_axiom_orchestration(query=query)

        response_payload = {
            "query": query,
            "session_id": payload.session_id,
            "target_master": result.get("target_master"),
            "target_capability": result.get("target_capability"),
            "confidence_score": result.get("confidence_score", 0.0),
            "current_step": result.get("current_step"),
            "clarification": result.get("clarification", {}),
            "memory_hit": result.get("memory_hit", False),
            "agent_task_input": result.get("agent_task_input", {}),
            "evidence_envelopes": result.get("evidence_envelopes", []),
            "visual_artifact": result.get("visual_artifact", {}),
            "final_output_markdown": result.get("final_output_markdown", "")
        }
        return response_payload
    except Exception as e:
        logger.error(f"Error executing chat orchestration: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/")
def serve_index():
    """Serves the modern Visual-First web application."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>AXIOM Multi-Agent Platform</h1><p>API is running. UI is initializing...</p>")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"Starting AXIOM Cloud Run Web Application on http://0.0.0.0:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
