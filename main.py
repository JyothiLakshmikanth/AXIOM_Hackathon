"""
AXIOM Orchestrator - FastAPI Entry Point for GCP Cloud Run
Unified 9-node LangGraph with PM.ai and ENG.ai masters.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from orchestrator.graph import AxiomCognitiveRunner
from orchestrator.state import AxiomState

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("axiom.cloud_run")

app = FastAPI(
    title="AXIOM Orchestrator",
    description="Unified 9-node LangGraph for PM.ai and ENG.ai masters",
    version="4.0"
)

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    query: str
    target_master: str
    resolved_intent: str
    confidence_score: float
    final_output_markdown: str
    structured_answer: Optional[Dict[str, Any]] = None
    visual_artifact: Optional[Dict[str, Any]] = None
    execution_time_ms: float
    session_id: str
    timestamp: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "4.0"}

@app.post("/query")
async def process_query(request: QueryRequest) -> QueryResponse:
    import time
    start_time = time.time()

    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        runner = AxiomCognitiveRunner()
        state: Dict[str, Any] = {
            "query": request.query,
            "session_id": request.session_id or f"session_{int(time.time())}",
            "user_id": request.user_id or "anonymous",
        }

        if request.context:
            state.update(request.context)

        result = runner.run(**state)
        execution_time_ms = (time.time() - start_time) * 1000

        return QueryResponse(
            query=request.query,
            target_master=result.get("target_master", "UNKNOWN"),
            resolved_intent=result.get("resolved_intent", "UNKNOWN"),
            confidence_score=float(result.get("confidence_score", 0.0)),
            final_output_markdown=result.get("final_output_markdown", ""),
            structured_answer=result.get("structured_answer"),
            visual_artifact=result.get("visual_artifact"),
            execution_time_ms=execution_time_ms,
            session_id=state["session_id"],
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/status")
async def service_status():
    return {
        "status": "running",
        "version": "4.0",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "capabilities": {
            "pm_master": True,
            "eng_master": True,
            "agent_selection": True,
            "evidence_caching": True,
            "cross_handoff": True,
            "hitl_checkpoint": True
        }
    }

@app.get("/")
async def root():
    return {"service": "AXIOM Orchestrator", "status": "running", "version": "4.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
