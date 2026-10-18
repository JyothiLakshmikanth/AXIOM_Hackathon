"""
Visual Generation Node for AXIOM.
Uses design_skills_engine to create visualization specs from evidence.
Invokes Nano Banana API for image generation.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from orchestrator.state import AxiomState, VisualArtifact
from orchestrator.design_skills_engine import VisualizationEngine, DesignSpecifications

logger = logging.getLogger("axiom.orchestrator.visual_gen")


import base64
from orchestrator.gemini_client import generate_gemini_content


def normalize_visual_type(visual_type: str, context: str = "") -> str:
    """Normalizes visualization type based on explicit type or context keywords."""
    combined = f"{visual_type} {context}".lower()
    if any(k in combined for k in ["fishbone", "ishikawa"]):
        return "fishbone"
    if any(k in combined for k in ["five_why", "5_why", "5 why", "five why", "causal chain", "5-why"]):
        return "five_why"
    if any(k in combined for k in ["leakage", "propagation", "leakage_propagation", "escape"]):
        return "leakage_propagation_chain"
    if any(k in combined for k in ["health_dashboard", "health dashboard", "risk cockpit", "cockpit"]):
        return "project_health_dashboard"
    if any(k in combined for k in ["timeline", "sprint_impact", "sprint impact", "heatmap", "workload"]):
        return "sprint_impact_timeline"
    if any(k in combined for k in ["flow", "process"]):
        return "flow"
    return "diagram"


def get_design_skill_spec(visual_type: str, context: str = "") -> Dict[str, Any]:
    """
    Returns concrete engineering design skill rules, orientation, coordinates,
    and semantic color palette for specialized diagrams (fishbone, 5-why, leakage chain, etc.)
    derived from DesignSpecifications in design_skills_engine.
    """
    norm_type = normalize_visual_type(visual_type, context)

    if norm_type == "fishbone":
        rules = """
- TYPE: Ishikawa / Fishbone Root Cause Analysis Diagram
- ORIENTATION: STRICTLY HORIZONTAL (Left to Right: Causes on Left → Central Horizontal Spine → Defect Head on Far Right).
- DIMENSIONS: viewBox="0 0 1200 700" width="1200" height="700"
- BACKGROUND: #0f172a (dark slate)
- CENTRAL SPINE: Horizontal bold line (x1="80" y1="350" x2="960" y2="350" stroke="#475569" stroke-width="4")
- DEFECT HEAD CONTAINER (Far Right):
  * Position: <rect x="960" y="260" width="210" height="180" rx="12" fill="#1e293b" stroke="#ef4444" stroke-width="3"/>
  * Header: <text x="1065" y="295" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">🚨 DEFECT HEAD</text>
  * Description: Summary of the defect/bug (e.g. TWK-107: Boundary-Zone Unlock Intermittently Fails)
- 4 CATEGORY DIAGONAL RIBS branching into the spine:
  1. Top-Left Rib (to x=380, y=350, stroke="#38bdf8", stroke-width="3"): "📋 Requirements & Specs"
  2. Bottom-Left Rib (to x=380, y=350, stroke="#ef4444", stroke-width="3"): "💻 Software Logic & AST (Root Cause)"
  3. Top-Right Rib (to x=780, y=350, stroke="#f59e0b", stroke-width="3"): "🧪 Testing & Verification"
  4. Bottom-Right Rib (to x=780, y=350, stroke="#10b981", stroke-width="3"): "⚙️ Process & Quality Gates"
- SUB-CAUSE CARDS: 2-3 rounded cards attached to each rib with short labels (3-8 words).
  * HIGHLIGHT ROOT CAUSE: On the Software Logic rib, give the root cause card a glowing red border (stroke="#ef4444" stroke-width="3") and target icon 🎯: "Strict > inequality operator rejects -65 dBm".
  * Requirements card: "REQ-L5-003 BLE RSSI threshold ambiguity".
  * Testing card: "TC-UNL-006 missed exact boundary edge".
  * Process card: "Rule #3: PR opened for HITL review".
"""
        system_prompt = "You are an expert enterprise systems architect generating a valid, raw SVG Ishikawa Fishbone diagram."

    elif norm_type == "five_why":
        rules = """
- TYPE: 5-Why Horizontal Causal Progression Ladder
- ORIENTATION: STRICTLY HORIZONTAL (Left to Right: Why 1 → Why 2 → Why 3 → Why 4 → Why 5 / Root Cause & Fix). NEVER vertical.
- DIMENSIONS: viewBox="0 0 1400 450" width="1400" height="450"
- BACKGROUND: #0f172a (dark slate)
- 5 CONNECTED STEPPED CARDS (y=160, height=150, width=230, rx="10"):
  1. Node 1 (x=30, stroke="#ef4444"): "🚨 WHY 1: Problem Symptom" -> Observable malfunction (e.g. Boundary unlock fails intermittently at boundary)
  2. Node 2 (x=310, stroke="#f97316"): "🔍 WHY 2: Subsystem Action" -> Proximity controller rejects phone key
  3. Node 3 (x=590, stroke="#f59e0b"): "⚠️ WHY 3: Logic Flaw" -> Evaluates strict inequality operator (rssi > threshold)
  4. Node 4 (x=870, stroke="#3b82f6"): "📋 WHY 4: Spec Gap" -> REQ-L5-003 boundary interpreted strictly instead of inclusive
  5. Node 5 (x=1150, stroke="#10b981", stroke-width="3", fill="#064e3b"): "🎯 WHY 5: Root Cause & Fix" -> Mutate AST to inclusive >= operator (PR #46)
- DIRECTIONAL CONNECTORS: Arrows between cards with "Why?" badges in the middle.
- COLOR PROGRESSION: Red (#ef4444) → Orange (#f97316) → Amber (#f59e0b) → Blue (#3b82f6) → Emerald Green (#10b981).
"""
        system_prompt = "You are an expert enterprise software architect generating a valid, raw SVG 5-Why causal chain diagram."

    elif norm_type == "leakage_propagation_chain":
        rules = """
- TYPE: Defect Leakage & Quality Gate Escape Propagation Chain
- ORIENTATION: STRICTLY HORIZONTAL (Left to Right: Inception Error → Code Defect → Verification Escape → Field Failure).
- DIMENSIONS: viewBox="0 0 1300 520" width="1300" height="520"
- BACKGROUND: #0f172a (dark slate)
- 4 PROGRESSION STAGE CARDS (y=110, height=170, width=265, rx="10", fill="#1e293b"):
  1. Stage 1 (x=40, stroke="#f59e0b"): "⚠️ 1. INCEPTION ERROR" -> Requirement boundary interpretation oversight.
  2. Stage 2 (x=350, stroke="#ef4444"): "🐞 2. CODE DEFECT" -> Strict > operator coded in proximity_controller.py.
  3. Stage 3 (x=660, stroke="#f97316"): "🧪 3. VERIFICATION ESCAPE" -> TC-UNL-006 test suite missed exact -65 dBm hit.
  4. Stage 4 (x=970, stroke="#dc2626", stroke-width="3", fill="#450a0a"): "🚨 4. OPERATIONAL FAILURE" -> Intermittent customer unlock failure at threshold.
- ESCAPE BARRIERS: Vertical dashed red lines between stages marking Quality Gate escapes.
- REMEDIATION BANNER (Bottom, x=40, y=340, width=1220, height=120, rx="12", fill="#064e3b", stroke="#10b981", stroke-width="2"):
  * Title: "🛡️ AXIOM CONTAINMENT & SURGICAL REMEDIATION"
  * Content: AST patch mutating > to >= deployed via PR #46, with regression test TC-ENR-007 verifying boundary hit.
"""
        system_prompt = "You are an expert enterprise quality engineer generating a valid, raw SVG Defect Leakage Propagation diagram."

    elif norm_type == "project_health_dashboard":
        rules = """
- TYPE: Executive Project Health & Delivery Risk Dashboard
- DIMENSIONS: viewBox="0 0 1300 650" width="1300" height="650"
- BACKGROUND: #0f172a
- 4 EXECUTIVE CARDS (grid layout with rounded corners rx="10", fill="#1e293b"):
  1. Schedule Health (stroke="#3b82f6"): Milestone timeline, sprint delivery progress
  2. Defect Density (stroke="#ef4444"): Open vs resolved defect rates, leakage trends
  3. Resource Capacity (stroke="#10b981"): Team utilization with 85% planned capacity ceiling line
  4. Top Delivery Risks (stroke="#f59e0b"): Prioritized risks and mitigation outlook
"""
        system_prompt = "You are an executive project management visualization engine generating a valid, raw SVG Dashboard."

    elif norm_type == "sprint_impact_timeline":
        rules = """
- TYPE: Team Workload & Sprint Capacity Heatmap Timeline
- ORIENTATION: STRICTLY HORIZONTAL (Past → Now → Future)
- DIMENSIONS: viewBox="0 0 1300 550" width="1300" height="550"
- BACKGROUND: #0f172a
- Central timeline spine with milestone markers (Planned=Blue, Delayed=Red, Complete=Green).
- Workload load bands: Light (🟢), Moderate (🟡), High Load (🔴) with 85% capacity threshold.
"""
        system_prompt = "You are an agile engineering operations engine generating a valid, raw SVG Timeline."

    else:
        rules = """
- TYPE: Enterprise Software Architecture & Defect Remediation Flow
- ORIENTATION: Clean Left-to-Right or Top-to-Bottom flow.
- DIMENSIONS: viewBox="0 0 1100 550" width="1100" height="550"
- BACKGROUND: #0f172a (dark slate), card fills: #1e293b, borders: #3b82f6 / #60a5fa, text: #f8fafc and #94a3b8
- 4 STAGES: Inbound Signal / Requirement → Proximity Controller Logic → AST Surgical Patch (PR #46) → Verification Test Suite
- ACCENT COLORS: Red (#ef4444) for defect, Green (#10b981) for patch/fix, Blue (#3b82f6) for controller.
"""
        system_prompt = "You are an expert enterprise software architecture visualization engine generating a valid, raw SVG diagram."

    return {
        "norm_type": norm_type,
        "rules": rules,
        "system_prompt": system_prompt
    }


def generate_svg_diagram_via_gemini(enriched_prompt: str, visual_type: str = "diagram") -> Optional[str]:
    """
    Generates a high-resolution, modern SVG diagram tailored with specialized
    engineering design skill rules (fishbone, 5-why, leakage propagation, etc.)
    using the unified Gemini LLM. Returns a data:image/svg+xml;base64,... URI.
    """
    spec = get_design_skill_spec(visual_type, enriched_prompt)
    norm_type = spec["norm_type"]
    rules = spec["rules"]
    system_prompt = spec["system_prompt"]

    prompt = f"""Generate a high-resolution, modern SVG diagram strictly applying the engineering design skill specifications below.

CONTEXT & TECHNICAL EVIDENCE:
{enriched_prompt}

DESIGN SKILL SPECIFICATIONS:
{rules}

STRICT SVG SYNTAX CONSTRAINTS:
1. Return ONLY raw, valid <svg xmlns="http://www.w3.org/2000/svg" ...>...</svg> markup.
2. Do NOT wrap in markdown code blocks (no ```svg or ```).
3. Do NOT include any introductory or conversational markdown text.
4. Keep the SVG self-contained and concise (< 120 SVG elements) so it closes cleanly with </svg>.
5. All text elements MUST have legible font sizes (Title: 22-26px bold, Headers: 14-16px bold, Labels: 11-13px).
"""
    try:
        logger.info(f"[GEMINI_SVG] Calling unified Gemini LLM with specialized design skill prompt for '{norm_type}'...")
        raw_svg = generate_gemini_content(prompt, system_prompt=system_prompt, timeout=35)
        clean = raw_svg.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
        if clean.endswith("```"):
            clean = clean.rsplit("\n", 1)[0] if "\n" in clean else clean[:-3]
        clean = clean.strip()

        start = clean.find("<svg")
        if start != -1:
            end = clean.rfind("</svg>")
            if end != -1:
                svg_content = clean[start:end+6]
            else:
                svg_content = clean[start:] + "\n</svg>"
            b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
            data_uri = f"data:image/svg+xml;base64,{b64}"
            logger.info(f"[GEMINI_SVG] Successfully generated '{norm_type}' SVG diagram via Gemini LLM ({len(svg_content)} chars)")
            return data_uri
    except Exception as e:
        logger.warning(f"[GEMINI_SVG] Gemini LLM SVG generation notice: {e}")
    return None


def generate_image(image_spec: Dict[str, Any]) -> Optional[str]:
    """
    Generates an image visualization using the same Gemini LLM (as SVG data URI),
    with fallbacks to Google Imagen, Vertex AI, Kroki, and Nano Banana.

    Args:
        image_spec: Dictionary with visualization specs (prompt, visual_type, summary, etc.)

    Returns:
        Image URI or base64 data URL (data:image/svg+xml;base64,...), or None if generation failed.
    """
    raw_prompt = image_spec.get("prompt") or image_spec.get("summary") or "Technical software architecture diagram"
    raw_visual_type = image_spec.get("visual_type", "diagram")

    # Clean and enrich the prompt for technical diagram generation
    clean_summary = str(raw_prompt).replace("\n", " ").strip()[:400]
    visual_type = normalize_visual_type(raw_visual_type, clean_summary)
    enriched_prompt = (
        f"A professional, clean high-resolution enterprise software {visual_type} technical diagram. "
        f"Modern clean UI style, readable architecture blocks, clear flow vectors: {clean_summary}"
    )

    # 1. Primary: Generate SVG Technical Diagram using the SAME Gemini LLM with specialized design skill prompt
    gemini_svg = generate_svg_diagram_via_gemini(enriched_prompt, visual_type)
    if gemini_svg:
        return gemini_svg

    # 2. Secondary: Google Image Generation via Gemini REST API
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        # 1a. Try official OpenAI-compatible endpoint (supports gemini-2.5-flash-image and imagen)
        openai_url = "https://generativelanguage.googleapis.com/v1beta/openai/images/generations"
        openai_headers = {
            "Authorization": f"Bearer {gemini_key}",
            "Content-Type": "application/json"
        }
        for img_model in ["gemini-2.5-flash-image", "imagen-3.0-generate-002"]:
            openai_payload = {
                "model": img_model,
                "prompt": enriched_prompt,
                "response_format": "b64_json",
                "n": 1
            }
            try:
                logger.info(f"[IMAGEN] Calling Google Image API ({img_model})...")
                res = requests.post(openai_url, json=openai_payload, headers=openai_headers, timeout=45)
                if res.status_code == 200:
                    data = res.json()
                    if "data" in data and len(data["data"]) > 0 and "b64_json" in data["data"][0]:
                        b64_data = data["data"][0]["b64_json"]
                        image_data_uri = f"data:image/png;base64,{b64_data}"
                        logger.info(f"[IMAGEN] Image generated successfully via Google ({img_model})")
                        return image_data_uri
                else:
                    logger.warning(f"[IMAGEN] Model {img_model} returned {res.status_code}: {res.text[:200]}")
            except Exception as e:
                logger.warning(f"[IMAGEN] Request to {img_model} failed: {e}")

        # 1b. Fallback to models:predict endpoint
        candidate_models = ["imagen-3.0-generate-002", "imagen-3.0-fast-generate-001"]
        for model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={gemini_key}"
            payload = {
                "instances": [{"prompt": enriched_prompt}],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "16:9",
                    "outputMimeType": "image/jpeg"
                }
            }
            try:
                logger.info(f"[IMAGEN] Calling Google predict API ({model})...")
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=45
                )
                if response.status_code == 200:
                    data = response.json()
                    predictions = data.get("predictions", [])
                    if predictions and "bytesBase64Encoded" in predictions[0]:
                        b64_data = predictions[0]["bytesBase64Encoded"]
                        mime = predictions[0].get("mimeType", "image/jpeg")
                        image_data_uri = f"data:{mime};base64,{b64_data}"
                        logger.info(f"[IMAGEN] Image generated successfully via Google ({model})")
                        return image_data_uri
                else:
                    logger.debug(f"[IMAGEN] Model {model} returned status {response.status_code}: {response.text[:200]}")
            except Exception as e:
                logger.debug(f"[IMAGEN] Imagen request to {model} failed: {e}")

    # 2. Secondary: Google Cloud Vertex AI Imagen REST API (direct IAM token on Cloud Run)
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or os.getenv("GCP_PROJECT_ID") or "axiom-510516"
    region = os.getenv("GCP_REGION", "us-central1")
    access_token = None

    # Try GCP metadata server (Cloud Run / GCE default service account)
    try:
        meta_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
        meta_resp = requests.get(meta_url, headers={"Metadata-Flavor": "Google"}, timeout=3)
        if meta_resp.status_code == 200:
            access_token = meta_resp.json().get("access_token")
            logger.info("[VERTEX_IMAGEN] Acquired access token from GCP Cloud Run metadata server.")
    except Exception:
        pass

    # Fallback to google.auth
    if not access_token:
        try:
            import google.auth
            import google.auth.transport.requests
            creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            creds.refresh(google.auth.transport.requests.Request())
            access_token = creds.token
            logger.info("[VERTEX_IMAGEN] Acquired access token via google.auth.")
        except Exception:
            pass

    if access_token and project_id:
        candidate_vertex_models = ["imagen-3.0-generate-002", "imagen-3.0-fast-generate-001", "imagegeneration@006"]
        for v_model in candidate_vertex_models:
            v_url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/{v_model}:predict"
            v_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            v_payload = {
                "instances": [{"prompt": enriched_prompt}],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "16:9",
                    "outputMimeType": "image/jpeg"
                }
            }
            try:
                logger.info(f"[VERTEX_IMAGEN] Calling Vertex AI REST endpoint for {v_model} (project={project_id}, region={region})...")
                v_resp = requests.post(v_url, json=v_payload, headers=v_headers, timeout=45)
                if v_resp.status_code == 200:
                    v_data = v_resp.json()
                    preds = v_data.get("predictions", [])
                    if preds and "bytesBase64Encoded" in preds[0]:
                        b64_data = preds[0]["bytesBase64Encoded"]
                        mime = preds[0].get("mimeType", "image/jpeg")
                        image_data_uri = f"data:{mime};base64,{b64_data}"
                        logger.info(f"[VERTEX_IMAGEN] Image generated successfully via Vertex AI ({v_model})")
                        return image_data_uri
                else:
                    logger.warning(f"[VERTEX_IMAGEN] Model {v_model} returned {v_resp.status_code}: {v_resp.text[:200]}")
            except Exception as e:
                logger.warning(f"[VERTEX_IMAGEN] Vertex AI request to {v_model} failed: {e}")

    # Fallback to Vertex AI SDK if available
    if project_id:
        try:
            import vertexai
            from vertexai.vision_models import ImageGenerationModel
            vertexai.init(project=project_id, location=region)
            sdk_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
            result = sdk_model.generate_images(prompt=enriched_prompt, number_of_images=1, aspect_ratio="16:9")
            if result and len(result) > 0 and hasattr(result[0], "_image_bytes"):
                b64 = base64.b64encode(result[0]._image_bytes).decode("utf-8")
                return f"data:image/jpeg;base64,{b64}"
        except Exception as e:
            logger.debug(f"[VERTEX_IMAGEN] Vertex AI SDK fallback skipped: {e}")

    # 3. Fallback: Nano Banana API (if NANO_BANANA_API_KEY is configured)
    nano_key = os.getenv("NANO_BANANA_API_KEY")
    if nano_key:
        try:
            url = "https://api.nanobana.na/generate"
            payload = {
                "model": image_spec.get("model", "stable-diffusion-v3"),
                "prompt": enriched_prompt,
                "width": image_spec.get("width", 1200),
                "height": image_spec.get("height", 700),
                "steps": image_spec.get("steps", 30),
                "guidance_scale": image_spec.get("guidance_scale", 7.5),
            }
            headers = {
                "Authorization": f"Bearer {nano_key}",
                "Content-Type": "application/json"
            }
            logger.info(f"[NANO_BANANA] Calling API: {enriched_prompt[:80]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                result = response.json()
                image_url = result.get("image_url") or result.get("data", {}).get("url")
                if image_url:
                    logger.info(f"[NANO_BANANA] Image generated: {image_url[:80]}...")
                    return image_url
            else:
                logger.warning(f"[NANO_BANANA] API error: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            logger.warning(f"[NANO_BANANA] Generation failed: {e}")

    # 4. Fallback: Convert Mermaid diagram to high-res SVG vector image via Kroki
    mermaid_def = image_spec.get("mermaid_diagram")
    if mermaid_def:
        try:
            clean_m = str(mermaid_def).strip().replace("```mermaid", "").replace("```", "").strip()
            resp = requests.post(
                "https://kroki.io/mermaid/svg",
                data=clean_m.encode("utf-8"),
                headers={"Content-Type": "text/plain; charset=utf-8"},
                timeout=8
            )
            if resp.status_code == 200 and resp.content:
                b64 = base64.b64encode(resp.content).decode("utf-8")
                svg_data_uri = f"data:image/svg+xml;base64,{b64}"
                logger.info("[VISUAL_GEN] Converted Mermaid flowchart into high-resolution SVG vector image URI.")
                return svg_data_uri
        except Exception as e:
            logger.debug(f"[VISUAL_GEN] SVG conversion skipped: {e}")

    logger.warning("[VISUAL_GEN] No visual generation provider succeeded; falling back to Mermaid diagram.")
    return None


# Backward-compatibility alias
generate_nano_banana_image = generate_image


def _create_visualization_from_evidence(
    evidence_envelopes: List[Dict[str, Any]],
    target_capability: str,
    query: str,
    visual_type: str
) -> Optional[Dict[str, Any]]:
    """
    Use design_skills_engine to create visualization spec from evidence.

    Args:
        evidence_envelopes: Collected evidence
        target_capability: Analysis type (e.g., "defect_triage", "RCA")
        query: User query
        visual_type: Type of visualization (fishbone, flow, diagram, etc.)

    Returns:
        Visualization spec with design params and image prompt
    """
    try:
        engine = VisualizationEngine()

        # Prepare evidence data for visualization
        evidence_data = {}
        for env in evidence_envelopes:
            artifact_type = env.get("artifact_type", "unknown")
            payload = env.get("payload", {})
            if artifact_type not in evidence_data:
                evidence_data[artifact_type] = []
            evidence_data[artifact_type].append(payload)

        # Generate visualization spec based on type
        viz_spec = None

        if visual_type == "fishbone":
            # RCA Ishikawa diagram
            root_cause = evidence_data.get("root_cause_analysis", [{}])[0]
            categories = root_cause.get("categories", {})
            viz_spec = engine.create_fishbone_diagram(
                defect=query,
                categories=categories
            )
        elif visual_type == "flow":
            # Process flow or leakage propagation
            viz_spec = engine.create_leakage_chain(
                error=evidence_data.get("defect_leakage_assessment", [{}])[0].get("error", ""),
                defect=evidence_data.get("github_issue_record", [{}])[0].get("title", ""),
                failure=evidence_data.get("test_run_failure_log", [{}])[0].get("failure", "")
            )
        elif visual_type == "timeline":
            # Project health or sprint timeline
            viz_spec = engine.create_timeline(
                milestones=evidence_data.get("sprint_velocity_record", [{}])[0].get("milestones", []),
                events=evidence_data.get("sprint_velocity_record", [{}])[0].get("events", [])
            )
        elif visual_type == "health_dashboard":
            # Project health dashboard
            viz_spec = engine.create_project_health_dashboard(
                schedule=evidence_data.get("schedule_metric", {}).get("status", "YELLOW"),
                quality=evidence_data.get("quality_metric", {}).get("status", "YELLOW"),
                resource=evidence_data.get("resource_metric", {}).get("status", "YELLOW"),
                scope=evidence_data.get("scope_metric", {}).get("status", "YELLOW")
            )
        else:
            # Generic diagram
            viz_spec = {
                "type": visual_type,
                "width": 1200,
                "height": 700,
                "design": DesignSpecifications.get_design(visual_type),
                "prompt": f"Professional {visual_type} diagram for: {query[:80]}"
            }

        return viz_spec

    except Exception as e:
        logger.warning(f"[VISUAL] Design skills engine failed: {e}")
        return None


def visual_generation_node(state: AxiomState) -> AxiomState:
    """
    Visual Generation Node: Creates images based on response_mode and design_skills_engine.

    Only executes if response_mode contains "image" (text_and_image or image_only).
    Uses design_skills_engine to create visualization specs from evidence.
    Invokes Nano Banana API for image generation.

    Args:
        state: Current AxiomState

    Returns:
        Updated state with visual_artifact
    """
    response_mode = state.get("response_mode", "text_only")

    # Check if visuals are requested
    if response_mode not in ("text_and_image", "image_only"):
        logger.info(f"[VISUAL_GEN] response_mode={response_mode}. Skipping image generation.")
        return state

    logger.info(f"[VISUAL_GEN] Starting image generation (response_mode={response_mode})")

    # Get evidence and visualization parameters
    evidence_envelopes = state.get("evidence_envelopes", [])
    structured_answer = state.get("structured_answer", {})
    target_capability = state.get("target_capability", "Analysis")
    query = state.get("query", "")
    visual_type = structured_answer.get("visual_type", "diagram")

    if not evidence_envelopes:
        logger.warning("[VISUAL_GEN] No evidence available; skipping visualization")
        state["visual_artifact"] = {"requires_visual": False}
        return state

    # Create visualization spec from evidence using design_skills_engine
    viz_spec = _create_visualization_from_evidence(
        evidence_envelopes,
        target_capability,
        query,
        visual_type
    )

    if not viz_spec:
        logger.warning("[VISUAL_GEN] Failed to create visualization spec")
        state["visual_artifact"] = {"requires_visual": False}
        return state

    # Prepare image generation spec for Nano Banana
    image_spec = {
        "model": "stable-diffusion-v3",
        "prompt": viz_spec.get("prompt", f"Professional {visual_type} visualization"),
        "width": viz_spec.get("width", 1200),
        "height": viz_spec.get("height", 700),
        "steps": 30,
        "guidance_scale": 7.5
    }

    # Generate image via Nano Banana
    image_url = generate_nano_banana_image(image_spec)

    # Update state with visual artifact
    state["visual_artifact"] = {
        "requires_visual": bool(image_url),
        "visual_type": visual_type,
        "image_url": image_url or "",
        "design_spec": viz_spec,
        "image_model": "nano-banana-stable-diffusion-v3",
        "generation_status": "COMPLETED" if image_url else "FAILED",
        "structured_caption": structured_answer.get("synthesis", "")[:100]
    }

    if image_url:
        logger.info(f"[VISUAL_GEN] Image generated: {image_url[:80]}...")

        # Inject into final markdown
        if state.get("final_output_markdown"):
            visual_banner = (
                f"\n\n### Visual Analysis ({visual_type.upper()})\n"
                f"> [!TIP]\n"
                f"> **Design-Driven Synthesis**: {state['visual_artifact'].get('structured_caption', '')}\n"
                f"![Analysis Visualization]({image_url})\n"
                f"*(Visual Asset Generated via Nano Banana Stable Diffusion)*\n"
            )
            state["final_output_markdown"] += visual_banner
    else:
        logger.warning("[VISUAL_GEN] Image generation failed; proceeding with text-only output")

    return state
