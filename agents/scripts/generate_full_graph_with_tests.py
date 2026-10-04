"""
Builds the complete, production-ready Knowledge Graph for Neo4j AuraDB.
Ingests:
1. data/requirements_master_v5.csv (Requirements with full text metadata)
2. data/test_cases_master_v5.csv (Test cases with full execution & specification metadata)
Produces:
1. data/neo4j_import_script.cypher (Ready to run in Neo4j AuraDB Workspace)
2. data/neo4j_graph_seed.json (For zero-dependency in-memory runtime execution)
"""

import csv
import json
import os
import re
from typing import Dict, Any, List, Set
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
REQ_CSV = os.path.join(DATA_DIR, "requirements_master_v5.csv")
TC_CSV = os.path.join(DATA_DIR, "test_cases_master_v5.csv")
CYPHER_OUT = os.path.join(DATA_DIR, "neo4j_import_script.cypher")
JSON_OUT = os.path.join(DATA_DIR, "neo4j_graph_seed.json")


def clean(s: str) -> str:
    if not s:
        return ""
    return s.strip().replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def extract_keywords(text: str) -> Set[str]:
    stopwords = {
        "the", "shall", "be", "to", "with", "a", "an", "and", "or", "in", "on", "of", "for",
        "by", "at", "is", "are", "from", "via", "that", "this", "their", "under", "all",
        "can", "will", "over", "only", "when", "if", "not", "into", "up", "as", "such"
    }
    words = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in stopwords}


def generate():
    with open(REQ_CSV, encoding="utf-8") as f:
        req_rows = list(csv.DictReader(f))

    with open(TC_CSV, encoding="utf-8") as f:
        tc_rows = list(csv.DictReader(f))

    cypher = []
    cypher.append("// ===========================================================================")
    cypher.append("// AXIOM KNOWLEDGE GRAPH: E-Key 2W Digital Key Platform")
    cypher.append("// Includes full test case details & requirement traceability")
    cypher.append("// Generated from requirements_master_v5.csv & test_cases_master_v5.csv")
    cypher.append("// ===========================================================================\n")

    # 1. Constraints & Indexes
    cypher.append("// --- 1. Indexes & Uniqueness Constraints ---")
    cypher.append("CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT test_case_id_unique IF NOT EXISTS FOR (t:TestCase) REQUIRE t.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT component_name_unique IF NOT EXISTS FOR (c:BusinessComponent) REQUIRE c.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT variant_id_unique IF NOT EXISTS FOR (v:Variant) REQUIRE v.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT oem_name_unique IF NOT EXISTS FOR (o:OEM) REQUIRE o.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT artifact_type_unique IF NOT EXISTS FOR (a:ArtifactType) REQUIRE a.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT verification_level_unique IF NOT EXISTS FOR (vl:VerificationLevel) REQUIRE vl.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT test_suite_id_unique IF NOT EXISTS FOR (ts:TestSuite) REQUIRE ts.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT test_plan_id_unique IF NOT EXISTS FOR (tp:TestPlan) REQUIRE tp.id IS UNIQUE;\n")

    # 2. Extract Column Entities
    artifact_types = set()
    verification_levels = set()
    business_components = set()
    variants = set()
    oems = set()
    test_suites = set()
    test_plans = set()

    for r in req_rows:
        art = r.get("Artifact Type", "").strip()
        if art:
            artifact_types.add(art)
        vl = r.get("Verification Level", "").strip()
        if vl:
            verification_levels.add(vl)
        bc = r.get("Business Component", "").strip()
        if bc:
            business_components.add(bc)
        for v in [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()]:
            variants.add(v)
        for o in [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()]:
            oems.add(o)

    for tc in tc_rows:
        ts = tc.get("Test Suite ID", "").strip()
        if ts:
            test_suites.add(ts)
        tp = tc.get("Test Plan ID", "").strip()
        if tp:
            test_plans.add(tp)
        for v in [x.strip() for x in tc.get("Target Variant", "").split(",") if x.strip()]:
            variants.add(v)

    # 3. Seed Column Nodes
    cypher.append("// --- 2. Seed Column Value Nodes ---")
    for a in sorted(artifact_types):
        cypher.append(f'MERGE (:ArtifactType {{name: "{clean(a)}"}});')
    for vl in sorted(verification_levels):
        cypher.append(f'MERGE (:VerificationLevel {{name: "{clean(vl)}"}});')
    for bc in sorted(business_components):
        cypher.append(f'MERGE (:BusinessComponent {{name: "{clean(bc)}"}});')
    for v in sorted(variants):
        cypher.append(f'MERGE (:Variant {{id: "{clean(v)}"}});')
    for o in sorted(oems):
        cypher.append(f'MERGE (:OEM {{name: "{clean(o)}"}});')
    for ts in sorted(test_suites):
        cypher.append(f'MERGE (:TestSuite {{id: "{clean(ts)}"}});')
    for tp in sorted(test_plans):
        cypher.append(f'MERGE (:TestPlan {{id: "{clean(tp)}"}});')
    cypher.append("")

    # 4. Seed Requirements with Full Text Metadata
    cypher.append("// --- 3. Seed Requirement Nodes with Rich Text Metadata ---")
    parent_map = defaultdict(list)
    kw_map = {}
    component_map = defaultdict(list)

    for r in req_rows:
        rid = clean(r.get("Requirement ID", ""))
        text = clean(r.get("Primary Text", ""))
        v_crit = clean(r.get("Verification Criteria", ""))
        notes = clean(r.get("Variant Implementation Notes", ""))
        status = clean(r.get("Status", ""))
        level = clean(r.get("Level", ""))

        cypher.append(
            f'MERGE (r:Requirement {{id: "{rid}"}}) '
            f'ON CREATE SET '
            f'r.primary_text = "{text}", '
            f'r.verification_criteria = "{v_crit}", '
            f'r.variant_implementation_notes = "{notes}", '
            f'r.status = "{status}", '
            f'r.level = "{level}";'
        )

        full_text = f"{text} {notes} {v_crit}"
        kw_map[rid] = extract_keywords(full_text)

        parent = r.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            parent_map[parent].append(r)

        bc = r.get("Business Component", "").strip()
        if bc:
            component_map[bc].append(rid)

    cypher.append("")

    # 5. Seed Test Cases with Full Execution & Specification Metadata
    cypher.append("// --- 4. Seed TestCase Nodes with Full Details from test_cases_master_v5.csv ---")
    for tc in tc_rows:
        tcid = clean(tc.get("Test Case ID", ""))
        desc = clean(tc.get("Test Description", ""))
        obj = clean(tc.get("Test Objective", ""))
        pre = clean(tc.get("Pre-conditions", ""))
        steps = clean(tc.get("Test Steps (Summary)", ""))
        exp = clean(tc.get("Expected Result", ""))
        ttype = clean(tc.get("Test Type", ""))
        prio = clean(tc.get("Priority", ""))
        status = clean(tc.get("Status", ""))
        owner = clean(tc.get("Owner", ""))
        suite = clean(tc.get("Test Suite ID", ""))
        plan = clean(tc.get("Test Plan ID", ""))

        cypher.append(
            f'MERGE (t:TestCase {{id: "{tcid}"}}) '
            f'ON CREATE SET '
            f't.description = "{desc}", '
            f't.objective = "{obj}", '
            f't.preconditions = "{pre}", '
            f't.steps = "{steps}", '
            f't.expected_result = "{exp}", '
            f't.test_type = "{ttype}", '
            f't.priority = "{prio}", '
            f't.status = "{status}", '
            f't.owner = "{owner}", '
            f't.suite_id = "{suite}", '
            f't.plan_id = "{plan}";'
        )
    cypher.append("")

    # 6. Direct Relationships
    cypher.append("// --- 5. DIRECT RELATIONSHIPS ---")
    # 6.1 Parent Hierarchy
    cypher.append("// 5.1 Parent-Child Decomposition")
    for r in req_rows:
        rid = clean(r.get("Requirement ID", ""))
        parent = r.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            parent_clean = clean(parent)
            cypher.append(
                f'MATCH (c:Requirement {{id: "{rid}"}}), (p:Requirement {{id: "{parent_clean}"}})\n'
                f'MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);'
            )

    # 6.2 Component Allocation
    cypher.append("\n// 5.2 Component Allocation (ALLOCATED_TO)")
    for r in req_rows:
        rid = clean(r.get("Requirement ID", ""))
        comp = r.get("Business Component", "").strip()
        if comp:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (c:BusinessComponent {{name: "{clean(comp)}"}})\n'
                f'MERGE (r)-[:ALLOCATED_TO]->(c);'
            )

    # 6.3 Variant Targeting
    cypher.append("\n// 5.3 Variant Targeting (TARGETS_VARIANT)")
    for r in req_rows:
        rid = clean(r.get("Requirement ID", ""))
        for v in [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (v:Variant {{id: "{clean(v)}"}})\n'
                f'MERGE (r)-[:TARGETS_VARIANT]->(v);'
            )

    # 6.4 OEM Customization
    cypher.append("\n// 5.4 OEM Customization (CUSTOMIZED_FOR_OEM)")
    for r in req_rows:
        rid = clean(r.get("Requirement ID", ""))
        for o in [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (o:OEM {{name: "{clean(o)}"}})\n'
                f'MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);'
            )

    # 6.5 Artifact Type & Verification Level
    cypher.append("\n// 5.5 Artifact Type & Verification Level")
    for r in req_rows:
        rid = clean(r.get("Requirement ID", ""))
        art = r.get("Artifact Type", "").strip()
        if art:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (a:ArtifactType {{name: "{clean(art)}"}})\n'
                f'MERGE (r)-[:IS_OF_TYPE]->(a);'
            )
        vl = r.get("Verification Level", "").strip()
        if vl:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (v:VerificationLevel {{name: "{clean(vl)}"}})\n'
                f'MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);'
            )

    # 6.6 Requirement-to-Test Traceability (Bidirectional)
    cypher.append("\n// 5.6 Requirement-to-Test Traceability (VERIFIED_BY and VERIFIES)")
    # From test_cases_master_v5.csv "Linked Req IDs"
    traceability_pairs = set()
    for tc in tc_rows:
        tcid = clean(tc.get("Test Case ID", ""))
        suite = clean(tc.get("Test Suite ID", ""))
        plan = clean(tc.get("Test Plan ID", ""))

        # Test Suite membership
        if suite:
            cypher.append(
                f'MATCH (t:TestCase {{id: "{tcid}"}}), (ts:TestSuite {{id: "{suite}"}})\n'
                f'MERGE (t)-[:BELONGS_TO_SUITE]->(ts);'
            )
        if plan:
            cypher.append(
                f'MATCH (t:TestCase {{id: "{tcid}"}}), (tp:TestPlan {{id: "{plan}"}})\n'
                f'MERGE (t)-[:BELONGS_TO_PLAN]->(tp);'
            )

        linked_reqs = [x.strip() for x in tc.get("Linked Req IDs", "").split(",") if x.strip()]
        for rid in linked_reqs:
            traceability_pairs.add((clean(rid), tcid))

    # Also from requirements_master_v5.csv "Test Cases Linked"
    for r in req_rows:
        rid = clean(r.get("Requirement ID", ""))
        linked_tcs = [x.strip() for x in r.get("Test Cases Linked", "").split(",") if x.strip()]
        for tc in linked_tcs:
            traceability_pairs.add((rid, clean(tc)))

    for rid, tcid in sorted(traceability_pairs):
        cypher.append(
            f'MATCH (r:Requirement {{id: "{rid}"}}), (t:TestCase {{id: "{tcid}"}})\n'
            f'MERGE (r)-[:VERIFIED_BY]->(t)\n'
            f'MERGE (t)-[:VERIFIES]->(r);'
        )
    cypher.append("")

    # 7. Semantic Relationships
    cypher.append("// ===========================================================================")
    cypher.append("// --- 6. DYNAMIC SEMANTIC RELATIONSHIPS ---")
    cypher.append("// ===========================================================================\n")

    # 7.1 Variant Divergence: Sibling requirements with same parent targeting different variants
    cypher.append("// 6.1 Variant Divergence (Sibling requirements targeting alternate variants)")
    semantic_edges_json = []
    for parent_id, children in parent_map.items():
        if len(children) > 1:
            for i in range(len(children)):
                for j in range(i + 1, len(children)):
                    c1 = children[i]
                    c2 = children[j]
                    v1 = set([x.strip() for x in c1.get("Target Variant", "").split(",") if x.strip()])
                    v2 = set([x.strip() for x in c2.get("Target Variant", "").split(",") if x.strip()])
                    if v1 != v2:
                        id1 = clean(c1["Requirement ID"])
                        id2 = clean(c2["Requirement ID"])
                        diff_desc = f"Variant divergence under {parent_id}: [{c1.get('Target Variant')}] vs [{c2.get('Target Variant')}]"
                        cypher.append(
                            f'MATCH (r1:Requirement {{id: "{id1}"}}), (r2:Requirement {{id: "{id2}"}})\n'
                            f'MERGE (r1)-[:VARIANT_DIVERGENCE_OF {{parent: "{parent_id}", rationale: "{diff_desc}"}}]->(r2)\n'
                            f'MERGE (r2)-[:VARIANT_DIVERGENCE_OF {{parent: "{parent_id}", rationale: "{diff_desc}"}}]->(r1);'
                        )
                        semantic_edges_json.append({"from": id1, "to": id2, "rel": "VARIANT_DIVERGENCE_OF", "parent": parent_id, "category": "semantic"})

    # 7.2 Component Co-Allocation
    cypher.append("\n// 6.2 Component Co-Allocation")
    for comp_name, req_ids in component_map.items():
        if comp_name != "System" and len(req_ids) > 1:
            for idx in range(min(12, len(req_ids) - 1)):
                r_a = req_ids[idx]
                r_b = req_ids[idx + 1]
                cypher.append(
                    f'MATCH (r1:Requirement {{id: "{r_a}"}}), (r2:Requirement {{id: "{r_b}"}})\n'
                    f'MERGE (r1)-[:CO_ALLOCATED_WITH {{component: "{clean(comp_name)}"}}]->(r2);'
                )
                semantic_edges_json.append({"from": r_a, "to": r_b, "rel": "CO_ALLOCATED_WITH", "component": comp_name, "category": "semantic"})

    # 7.3 Semantic Topic Affinity
    cypher.append("\n// 6.3 Semantic Domain Affinity")
    req_ids_list = list(kw_map.keys())
    critical_topics = {"proximity", "unlock", "lock", "ble", "uwb", "encryption", "offline", "grace", "revocation", "telemetry", "biometric", "valet", "speed", "jwt", "tls"}
    for i in range(len(req_ids_list)):
        for j in range(i + 1, len(req_ids_list)):
            r1 = req_ids_list[i]
            r2 = req_ids_list[j]
            k1 = kw_map[r1]
            k2 = kw_map[r2]
            intersection = k1.intersection(k2)
            matched_critical = intersection.intersection(critical_topics)
            if len(matched_critical) >= 2 or (len(intersection) >= 4 and len(matched_critical) >= 1):
                shared_kw = ", ".join(sorted(matched_critical if matched_critical else list(intersection)[:3]))
                score = round(len(intersection) / max(1, len(k1.union(k2))), 3)
                cypher.append(
                    f'MATCH (r1:Requirement {{id: "{r1}"}}), (r2:Requirement {{id: "{r2}"}})\n'
                    f'MERGE (r1)-[:SEMANTIC_AFFINITY {{shared_topics: "{shared_kw}", score: {score}}}]->(r2)\n'
                    f'MERGE (r2)-[:SEMANTIC_AFFINITY {{shared_topics: "{shared_kw}", score: {score}}}]->(r1);'
                )
                semantic_edges_json.append({"from": r1, "to": r2, "rel": "SEMANTIC_AFFINITY", "topics": shared_kw, "score": score, "category": "semantic"})

    # 8. Verification Queries
    cypher.append("\n// --- 7. Verification Summary Queries ---")
    cypher.append("MATCH (n) RETURN labels(n) as EntityType, count(*) as NodeCount ORDER BY NodeCount DESC;")
    cypher.append("MATCH ()-[r]->() RETURN type(r) as RelationshipType, count(*) as EdgeCount ORDER BY EdgeCount DESC;")

    # Write output Cypher script
    with open(CYPHER_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(cypher))

    print(f"Generated Cypher script: {CYPHER_OUT}")

    # Build full JSON seed
    nodes_json = {}
    edges_json = []

    # Requirements
    for r in req_rows:
        rid = r["Requirement ID"].strip()
        nodes_json[rid] = {
            "id": rid,
            "label": "Requirement",
            "primary_text": r.get("Primary Text", "").strip(),
            "verification_criteria": r.get("Verification Criteria", "").strip(),
            "variant_implementation_notes": r.get("Variant Implementation Notes", "").strip(),
            "status": r.get("Status", "").strip(),
            "level": r.get("Level", "").strip(),
            "artifact_type": r.get("Artifact Type", "").strip(),
            "verification_level": r.get("Verification Level", "").strip(),
            "component": r.get("Business Component", "").strip(),
            "target_variants": [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()],
            "oems": [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()],
            "test_cases": [x.strip() for x in r.get("Test Cases Linked", "").split(",") if x.strip()]
        }

    # Test Cases
    for tc in tc_rows:
        tcid = tc["Test Case ID"].strip()
        nodes_json[tcid] = {
            "id": tcid,
            "label": "TestCase",
            "description": tc.get("Test Description", "").strip(),
            "objective": tc.get("Test Objective", "").strip(),
            "preconditions": tc.get("Pre-conditions", "").strip(),
            "steps": tc.get("Test Steps (Summary)", "").strip(),
            "expected_result": tc.get("Expected Result", "").strip(),
            "test_type": tc.get("Test Type", "").strip(),
            "priority": tc.get("Priority", "").strip(),
            "status": tc.get("Status", "").strip(),
            "owner": tc.get("Owner", "").strip(),
            "target_variants": [x.strip() for x in tc.get("Target Variant", "").split(",") if x.strip()],
            "suite_id": tc.get("Test Suite ID", "").strip(),
            "plan_id": tc.get("Test Plan ID", "").strip(),
            "linked_requirements": [x.strip() for x in tc.get("Linked Req IDs", "").split(",") if x.strip()]
        }

    # Direct edges
    for r in req_rows:
        rid = r["Requirement ID"].strip()
        parent = r.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            edges_json.append({"from": rid, "rel": "CHILD_OF", "to": parent, "category": "direct"})
            edges_json.append({"from": parent, "rel": "PARENT_OF", "to": rid, "category": "direct"})

        comp = r.get("Business Component", "").strip()
        if comp:
            cid = f"COMP-{comp.replace(' ', '_').upper()}"
            if cid not in nodes_json:
                nodes_json[cid] = {"id": cid, "label": "BusinessComponent", "name": comp}
            edges_json.append({"from": rid, "rel": "ALLOCATED_TO", "to": cid, "category": "direct"})

        for v in [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()]:
            vid = f"VAR-{v.replace('VAR-', '')}"
            if vid not in nodes_json:
                nodes_json[vid] = {"id": vid, "label": "Variant", "name": v}
            edges_json.append({"from": rid, "rel": "TARGETS_VARIANT", "to": vid, "category": "direct"})

        for o in [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()]:
            oid = f"OEM-{o.replace(' ', '_').upper()}"
            if oid not in nodes_json:
                nodes_json[oid] = {"id": oid, "label": "OEM", "name": o}
            edges_json.append({"from": rid, "rel": "CUSTOMIZED_FOR_OEM", "to": oid, "category": "direct"})

    # Traceability edges
    for rid, tcid in sorted(traceability_pairs):
        edges_json.append({"from": rid, "rel": "VERIFIED_BY", "to": tcid, "category": "direct"})
        edges_json.append({"from": tcid, "rel": "VERIFIES", "to": rid, "category": "direct"})

    # Add semantic edges
    edges_json.extend(semantic_edges_json)

    seed_data = {
        "metadata": {
            "title": "AXIOM Comprehensive Knowledge Graph (Requirements & Test Cases)",
            "total_nodes": len(nodes_json),
            "total_edges": len(edges_json),
            "requirements_count": len(req_rows),
            "test_cases_count": len(tc_rows),
            "direct_edges": sum(1 for e in edges_json if e.get("category") == "direct"),
            "semantic_edges": sum(1 for e in edges_json if e.get("category") == "semantic")
        },
        "nodes": nodes_json,
        "edges": edges_json
    }

    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2)

    print(f"Generated JSON seed: {JSON_OUT}")
    return seed_data


if __name__ == "__main__":
    generate()
