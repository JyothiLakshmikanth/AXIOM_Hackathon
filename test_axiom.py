#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick AXIOM Functionality Test Script
Tests routing, master selection, visual synthesis, and full orchestration
"""

import sys
import json
import logging
from typing import Dict, Any

# Fix encoding for Windows terminals
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("axiom.test")

# Import AXIOM components
try:
    from orchestrator.router import analyze_intent
    from orchestrator.state import AxiomState
    from orchestrator.graph import run_axiom_orchestration
    logger.info("✅ Successfully imported AXIOM components")
except ImportError as e:
    logger.error(f"❌ Failed to import AXIOM: {e}")
    sys.exit(1)


def test_router(query: str) -> Dict[str, Any]:
    """Test a single query through the router only"""
    try:
        return analyze_intent(query)
    except Exception as e:
        print(f"❌ Router Error: {e}")
        return {"error": str(e)}


def test_full_orchestration(query: str, test_name: str) -> Dict[str, Any]:
    """Test a query through full AXIOM orchestration (includes visual synthesis)"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print(f"QUERY: {query}")
    print("="*80)
    
    try:
        result = run_axiom_orchestration(query=query)
        
        master = result.get("target_master", "Router")
        capability = result.get("target_capability", "N/A")
        
        print(f"\n✅ Full Orchestration Result:")
        print(f"   Target Master: {master}")
        print(f"   Target Capability: {capability}")
        print(f"   Confidence Score: {result.get('confidence_score', 0):.2f}")
        
        # Check for visual synthesis
        visual = result.get("visual_artifact", {})
        if visual and visual.get("requires_visual"):
            print(f"\n🎨 Visual Synthesis:")
            print(f"   Type: {visual.get('visual_type', 'N/A')}")
            print(f"   Caption: {visual.get('structured_caption', 'N/A')}")
            if visual.get("fallback_mermaid"):
                print(f"   Mermaid (fallback):")
                for line in visual.get("fallback_mermaid", "").split("\n"):
                    if line.strip():
                        print(f"      {line}")
        else:
            print(f"\n🎨 Visual Synthesis: Not required for this query")
        
        # Check for evidence
        evidences = result.get("evidence_envelopes", [])
        if evidences:
            print(f"\n📋 Evidence Envelopes: {len(evidences)} found")
            for env in evidences:
                print(f"   - {env.get('artifact_id', 'unknown')}: {env.get('artifact_type', 'unknown')}")
        
        return result
    except Exception as e:
        print(f"❌ Orchestration Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def test_query(query: str, test_name: str) -> Dict[str, Any]:
    """Test a single query through the router"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print(f"QUERY: {query}")
    print("="*80)
    
    try:
        result = analyze_intent(query)
        
        print(f"\n✅ Router Result:")
        print(f"   Clarification Needed: {result.get('clarification_needed', False)}")
        print(f"   Target Master: {result.get('target_master', 'N/A')}")
        print(f"   Target Capability: {result.get('target_capability', 'N/A')}")
        print(f"   Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"   Reasoning: {result.get('reasoning_summary', 'N/A')}")
        
        if result.get('clarification_needed'):
            print(f"\n❓ Clarification Questions:")
            for i, q in enumerate(result.get('clarification_questions', []), 1):
                print(f"   {i}. {q}")
        
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def main():
    """Run test suite"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  AXIOM Multi-Agent Intelligence System - Test Suite".center(78) + "║")
    print("║" + "  Testing Router, Master Selection & Visual Synthesis".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Test Suite
    tests = [
        (
            "What is the blast radius and defect triage for GH-ISSUE-107?",
            "AXIOM-PM: Defect Triage Query"
        ),
        (
            "Perform deep code RCA and generate surgical patch for proximity_controller.py",
            "AXIOM-ENG: Code RCA & Patch Generation"
        ),
        (
            "Sprint 4 is slipping by 18 story points, how should we replan?",
            "AXIOM-PM: Sprint Replanning Query"
        ),
        (
            "What test coverage gaps exist for the BLE unlock feature?",
            "AXIOM-ENG: Test Coverage Analysis"
        ),
        (
            "Base variant fails passive unlock when BLE RSSI drops below threshold",
            "AXIOM-PM: Requirement Impact Analysis"
        ),
        (
            "fix something",
            "AXIOM: Ambiguous Query (Should Request Clarification)"
        ),
        (
            "hi",
            "AXIOM: Vague Query (Should Request Clarification)"
        ),
        (
            "Perform 8D problem solving for the proximity_controller hysteresis bug",
            "AXIOM-ENG: Eight Disciplines Analysis"
        ),
        (
            "Generate pytest test cases for edge cases in unlock logic",
            "AXIOM-ENG: Test Generation"
        ),
        (
            "What is the project health scorecard and delivery forecast?",
            "AXIOM-PM: Project Health Query"
        ),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for query, test_name in tests:
        result = test_query(query, test_name)
        results.append({
            "test": test_name,
            "query": query,
            "result": result
        })
        
        if "error" not in result:
            passed += 1
        else:
            failed += 1
    
    # Test visual synthesis with a sample AXIOM-PM query
    print("\n\n" + "="*80)
    print("VISUAL SYNTHESIS TEST")
    print("="*80)
    print("Testing full orchestration with visual synthesis generation...")
    
    visual_query = "What is the blast radius and defect triage for GH-ISSUE-107?"
    visual_result = test_full_orchestration(visual_query, "AXIOM-PM: Full Orchestration with Visual Synthesis")
    
    if "error" not in visual_result:
        passed += 1
        print("\n✅ Visual Synthesis Test: PASSED")
    else:
        failed += 1
        print("\n❌ Visual Synthesis Test: FAILED")
    
    # Summary Report
    print("\n\n" + "="*80)
    print("TEST SUMMARY REPORT")
    print("="*80)
    
    total_tests = len(tests) + 1  # +1 for visual synthesis test
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {total_tests}")
    print(f"✨ Success Rate: {(passed/total_tests*100):.1f}%")
    
    # Master Distribution
    print("\n\nROUTING DISTRIBUTION:")
    axiom_pm_count = sum(1 for r in results if r['result'].get('target_master') == 'AXIOM-PM')
    axiom_eng_count = sum(1 for r in results if r['result'].get('target_master') == 'AXIOM-ENG')
    clarification_count = sum(1 for r in results if r['result'].get('clarification_needed'))
    
    print(f"   🛡️  AXIOM-PM (Project Management): {axiom_pm_count}")
    print(f"   ⚡ AXIOM-ENG (Engineering): {axiom_eng_count}")
    print(f"   ❓ Clarification Required: {clarification_count}")
    
    # Capability Distribution
    print("\n\nCAPABILITY DISTRIBUTION:")
    capabilities = {}
    for r in results:
        cap = r['result'].get('target_capability', 'N/A')
        if cap != 'N/A':
            capabilities[cap] = capabilities.get(cap, 0) + 1
    
    for cap, count in sorted(capabilities.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {cap}: {count}")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
