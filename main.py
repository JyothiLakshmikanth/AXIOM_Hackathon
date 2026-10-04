"""
AXIOM: Multi-Agent Intelligence System - Main CLI Entry Point.
Allows running one-shot queries or interactive cognitive sessions with PM.ai and ENG.ai Masters.
"""

import sys
import json
import logging
from typing import Dict, Any

# Ensure stdout handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from orchestrator.graph import run_axiom_orchestration
from orchestrator.state import AxiomState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("axiom.main")


def print_banner():
    banner = """
================================================================================
       _    __  _____ ___  __  __
      / \\   \\ \\/ /_ _/ _ \\|  \\/  |   AXIOM: Multi-Agent Intelligence Platform
     / _ \\   \\  / | | | | | |\\/| |   Masters: PM.ai & ENG.ai
    / ___ \\  /  \\ | | |_| | |  | |   Grounding: Neo4j KG | Firestore | Qdrant
   /_/   \\_\\/_/\\_\\___\\___/|_|  |_|   Deployment: Google Cloud Platform (Cloud Run)
================================================================================
"""
    print(banner)


def display_result(result: Dict[str, Any]):
    print("\n" + "=" * 80)
    print(f"ROUTER CLASSIFICATION: Target Master = {result.get('target_master')} | Capability = {result.get('target_capability')}")
    print(f"CONFIDENCE SCORE      : {result.get('confidence_score', 0.0):.2f}")
    print(f"CURRENT STEP          : {result.get('current_step')}")
    print("=" * 80)

    # Check clarification
    clarification = result.get("clarification", {})
    if clarification.get("clarification_needed"):
        print("\n[!] INTENT CLARIFICATION NEEDED:")
        print(f"Reason: {clarification.get('ambiguity_reason')}")
        print("\nPlease clarify with one of the following:")
        for i, q in enumerate(clarification.get("clarification_questions", []), 1):
            print(f"  {i}. {q}")
        print("\n" + "-" * 80)
        return

    # Check Memory Hit
    if result.get("memory_hit"):
        print("\n[+] FIRESTORE MEMORY HIT: Reused previously verified EvidenceEnvelopes (skipped specialized agent call).")

    # Delegated agent details
    agent_info = result.get("agent_task_input", {})
    if agent_info:
        print(f"\n[+] DELEGATED SPECIALIZED AGENT: {agent_info.get('executed_agent')}")
        print(f"    Summary: {agent_info.get('summary')}")

    # Evidence Envelopes
    evidences = result.get("evidence_envelopes", [])
    print(f"\n[+] EVIDENCE ENVELOPES ACCUMULATED: {len(evidences)}")
    for env in evidences:
        print(f"    - [{env.get('source_system')}] {env.get('artifact_id')} ({env.get('artifact_type')}) - Status: {env.get('quality_status')}")

    # Visual Artifact
    visual = result.get("visual_artifact", {})
    if visual.get("requires_visual"):
        print(f"\n[+] VISUAL-FIRST PRESENTATION: Model={visual.get('image_model')} | Status={visual.get('generation_status')}")
        print(f"    Asset URI: {visual.get('image_url')}")
        print(f"    Caption  : {visual.get('structured_caption')}")

    # Final Output Markdown
    print("\n" + "-" * 80)
    print("FINAL STRUCTURED RESPONSE:")
    print("-" * 80)
    print(result.get("final_output_markdown", "No output generated."))
    print("=" * 80 + "\n")


def interactive_loop():
    print_banner()
    print("Type your inquiry or scenario below. Type 'exit' or 'quit' to stop.\n")
    print("Quick test examples:")
    print("  1. 'What is the blast radius and defect triage for GH-ISSUE-107?' (PM.ai)")
    print("  2. 'Perform deep code RCA and generate surgical patch for proximity_controller.py' (ENG.ai)")
    print("  3. 'Base variant fails passive unlock when BLE RSSI drops below threshold' (Requirement Agent via Neo4j KG)")
    print("  4. 'Sprint 4 is slipping by 18 story points, how should we replan?' (PM.ai)")
    print("  5. 'hi' or 'fix something' (Tests Ambiguous Intent Clarification Router)\n")

    while True:
        try:
            query = input("AXIOM > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Exiting AXIOM. Goodbye!")
                break

            result = run_axiom_orchestration(query=query)
            display_result(result)

        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break
        except Exception as e:
            logger.error(f"Error during orchestration: {e}", exc_info=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # One-shot CLI query mode
        query = " ".join(sys.argv[1:])
        print_banner()
        print(f"Processing Query: '{query}'\n")
        res = run_axiom_orchestration(query=query)
        display_result(res)
    else:
        # Interactive CLI mode
        interactive_loop()
