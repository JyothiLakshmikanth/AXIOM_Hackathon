"""
AXIOM Gemini LLM Client.
Unified, resilient client for Google Gemini via Direct API and Vertex AI.
Guarantees observable execution, explicit logging, and loud failure modes.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("axiom.orchestrator.gemini")

DEFAULT_GEMINI_API_KEY = "AQ.Ab8RN6KVtoHm0-SlVOsZuuoGJypnNSxVXBXfPoXc0wcXJ22DsQ"


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment or fallback to verified key."""
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or DEFAULT_GEMINI_API_KEY
    )


_LAST_LLM_METRICS: Dict[str, Any] = {
    "provider": None,
    "model": None,
    "latency_s": None,
    "status": None,
    "chars_returned": 0
}


def get_last_llm_metrics() -> Dict[str, Any]:
    """Return telemetry metrics from the most recent LLM execution."""
    return dict(_LAST_LLM_METRICS)


def call_gemini_api_key(
    prompt: str,
    system_prompt: str = "",
    json_mode: bool = False,
    timeout: int = 35
) -> str:
    """
    Direct HTTPS call to Google Generative Language API using API Key.
    Uses standard requests to ensure zero package conflicts.
    """
    import requests

    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("No Gemini API key available.")

    candidate_models = [
        os.getenv("GEMINI_API_MODEL", "gemini-flash-lite-latest"),
        "gemini-flash-latest",
        "gemini-3.8-flash"
    ]

    # Combine system prompt and user prompt
    full_prompt = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192
        }
    }
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    last_error = None
    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        logger.info(f"[LLM] Calling Gemini API | Model: {model} | JSON Mode: {json_mode}")
        print(f"[LLM DEBUG] Starting Gemini API call | Model: {model} | Prompt length: {len(full_prompt)} chars", flush=True)

        t0 = time.time()
        try:
            r = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            elapsed = time.time() - t0

            if r.status_code == 200:
                data = r.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"[LLM] Gemini response received in {elapsed:.2f}s | Length: {len(text)} chars")
                print(f"[LLM DEBUG] Gemini response received in {elapsed:.2f}s | Output: {len(text)} chars", flush=True)

                _LAST_LLM_METRICS.update({
                    "provider": "Google Gemini API (API Key)",
                    "model": model,
                    "latency_s": round(elapsed, 2),
                    "status": "SUCCESS",
                    "chars_returned": len(text)
                })
                return text
            else:
                err_text = r.text[:200]
                logger.warning(f"[LLM] Model {model} returned status {r.status_code}: {err_text}")
                print(f"[LLM DEBUG] Model {model} returned status {r.status_code}: {err_text}", flush=True)
                last_error = RuntimeError(f"Gemini API ({model}) status {r.status_code}: {err_text}")

        except Exception as e:
            elapsed = time.time() - t0
            logger.warning(f"[LLM] Model {model} request failed after {elapsed:.2f}s: {e}")
            print(f"[LLM DEBUG] Model {model} request failed ({e})", flush=True)
            last_error = e

    raise RuntimeError(f"All Gemini API models failed. Last error: {last_error}")


def call_vertex_ai(
    prompt: str,
    system_prompt: str = "",
    model_name: Optional[str] = None
) -> str:
    """
    Call Vertex AI via ChatVertexAI on Google Cloud project.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT is not set.")

    model = model_name or os.getenv("VERTEX_AI_GEMINI_MODEL", "gemini-1.5-flash-001")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    logger.info(f"[LLM] Calling Vertex AI | Project: {project_id} | Location: {location} | Model: {model}")

    from langchain_google_vertexai import ChatVertexAI
    from langchain_core.messages import SystemMessage, HumanMessage

    llm = ChatVertexAI(
        model_name=model,
        temperature=0.2,
        project=project_id,
        location=location
    )

    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))

    t0 = time.time()
    response = llm.invoke(messages)
    elapsed = time.time() - t0
    text = response.content
    logger.info(f"[LLM] Vertex AI response received in {elapsed:.2f}s | Length: {len(text)} chars")
    print(f"[LLM DEBUG] Vertex AI response received in {elapsed:.2f}s | Output: {len(text)} chars", flush=True)

    _LAST_LLM_METRICS.update({
        "provider": "Google Vertex AI (GCP IAM)",
        "model": model,
        "latency_s": round(elapsed, 2),
        "status": "SUCCESS",
        "chars_returned": len(text)
    })
    return text


def generate_gemini_content(
    prompt: str,
    system_prompt: str = "",
    json_mode: bool = False,
    timeout: int = 35
) -> str:
    """
    Unified entry point for Gemini execution.
    Prioritizes Gemini API (fast, reliable key), falls back to Vertex AI.
    Logs execution transparently and fails loudly if both fail.
    """
    errors = []

    # Priority 1: Gemini API via API Key
    api_key = get_gemini_api_key()
    if api_key:
        try:
            return call_gemini_api_key(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=json_mode,
                timeout=timeout
            )
        except Exception as e:
            logger.warning(f"[LLM] Gemini API Key engine failed: {e}. Attempting Vertex AI failover...")
            errors.append(f"Gemini API: {e}")

    # Priority 2: Vertex AI via GCP project IAM
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    if project_id:
        try:
            return call_vertex_ai(
                prompt=prompt,
                system_prompt=system_prompt
            )
        except Exception as e:
            logger.warning(f"[LLM] Vertex AI engine failed: {e}")
            errors.append(f"Vertex AI: {e}")

    # If both failed, log loudly and raise
    full_error_msg = " | ".join(errors) if errors else "No LLM credentials (API key or project) configured."
    logger.error(f"[LLM ERROR] All Gemini synthesis providers failed: {full_error_msg}")
    raise RuntimeError(f"Gemini LLM invocation failed: {full_error_msg}")
