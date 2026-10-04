"""
Generates Neo4j Cypher Import Script and JSON seed data from
data/requirements_master_v5.csv and data/test_cases_master_v5.csv.
"""

import csv
import json
import os
import re

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
REQ_CSV = os.path.join(DATA_DIR, "requirements_master_v5.csv")
TC_CSV = os.path.join(DATA_DIR, "test_cases_master_v5.csv")
OUTPUT_CYPHER = os.path.join(DATA_DIR, "neo4j_import_script.cypher")
OUTPUT_JSON = os.path.join(DATA_DIR, "neo4j_graph_seed.json")


def clean_str(val: str) -> str:
    if not val:
        return ""
    return val.strip().replace("'", "\\'").replace('"', '\\"')


def main():
    print(f"Reading requirements from {REQ_CSV}...")
    with open(REQ_CSV, encoding="utf-8") as f:
        req_rows = list(csv.DictReader(f))

    print(f"Reading test cases from {TC_CSV}...")
    with open(TC_CSV, encoding="utf-8") as f:
        tc_rows = list(csv.DictReader(f))

    cypher_lines = [
        "// =================================================================",
        "// AXIOM Knowledge Graph Initialization & Ingestion Script",
        "// System: E-Key 2W Digital Key Platform",
        "// Nodes: Requirement, TestCase, Component, Variant, OEM",
        "// Edges: CHILD_OF, VERIFIED_BY, ALLOCATED_TO, TARGETS_VARIANT, APPLICABLE_TO_OEM",
        "// =================================================================",
        "",
        "// --- 1. Unique Constraints & Indexes ---",
        "CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE;",
        "CREATE CONSTRAINT test_case_id_unique IF NOT EXISTS FOR (t:TestCase) REQUIRE t.id IS UNIQUE;",
        "CREATE CONSTRAINT component_name_unique IF NOT EXISTS FOR (c:Component) REQUIRE c.name IS UNIQUE;",
        "CREATE CONSTRAINT variant_id_unique IF NOT EXISTS FOR (v:Variant) REQUIRE v.id IS UNIQUE;",
        "CREATE CONSTRAINT oem_name_unique IF NOT EXISTS FOR (o:OEM) REQUIRE o.name IS UNIQUE;",
        "",
        "// --- 2. Seed Component Nodes ---",
    ]

    components = set()
    variants = set()
    oems = set()

    for r in req_rows:
        comp = r.get("Business Component", "").strip()
        if comp:
            components.add(comp)
        vars_str = r.get("Target Variant", "")
        for v in [x.strip() for x in vars_str.split(",") if x.strip()]:
            variants.add(v)
        oems_str = r.get("OEM Customization Flag", "")
        for o in [x.strip() for x in oems_str.split(",") if x.strip()]:
            oems.add(o)

    for c in sorted(components):
        cypher_lines.append(f'MERGE (c:Component {{name: "{clean_str(c)}"}});')

    cypher_lines.append("\n// --- 3. Seed Variant Nodes ---")
    for v in sorted(variants):
        cypher_lines.append(f'MERGE (v:Variant {{id: "{clean_str(v)}"}});')

    cypher_lines.append("\n// --- 4. Seed OEM Nodes ---")
    for o in sorted(oems):
        cypher_lines.append(f'MERGE (o:OEM {{name: "{clean_str(o)}"}});')

    cypher_lines.append("\n// --- 5. Seed Test Cases ---")
    for tc in tc_rows:
        tc_id = clean_str(tc.get("Test Case ID", ""))
        desc = clean_str(tc.get("Test Description", ""))
        t_type = clean_str(tc.get("Test Type", ""))
        prio = clean_str(tc.get("Priority", ""))
        status = clean_str(tc.get("Status", ""))
        owner = clean_str(tc.get("Owner", ""))
        suite = clean_str(tc.get("Test Suite ID", ""))
        plan = clean_str(tc.get("Test Plan ID", ""))

        cypher_lines.append(
            f'MERGE (t:TestCase {{id: "{tc_id}"}}) '
            f'ON CREATE SET t.description = "{desc}", t.type = "{t_type}", '
            f't.priority = "{prio}", t.status = "{status}", t.owner = "{owner}", '
            f't.suite_id = "{suite}", t.plan_id = "{plan}";'
        )

    cypher_lines.append("\n// --- 6. Seed Requirements & Relationships ---")
    for req in req_rows:
        req_id = clean_str(req.get("Requirement ID", ""))
        art_type = clean_str(req.get("Artifact Type", ""))
        text = clean_str(req.get("Primary Text", ""))
        v_crit = clean_str(req.get("Verification Criteria", ""))
        v_lvl = clean_str(req.get("Verification Level", ""))
        status = clean_str(req.get("Status", ""))
        level = clean_str(req.get("Level", ""))
        notes = clean_str(req.get("Variant Implementation Notes", ""))

        cypher_lines.append(
            f'MERGE (r:Requirement {{id: "{req_id}"}}) '
            f'ON CREATE SET r.text = "{text}", r.artifact_type = "{art_type}", '
            f'r.verification_criteria = "{v_crit}", r.verification_level = "{v_lvl}", '
            f'r.status = "{status}", r.level = "{level}", r.notes = "{notes}";'
        )

        # Hierarchy / Parent edge
        parent = req.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            cypher_lines.append(
                f'MATCH (child:Requirement {{id: "{req_id}"}}), (parent:Requirement {{id: "{clean_str(parent)}"}})\n'
                f'MERGE (child)-[:CHILD_OF]->(parent);'
            )

        # Component allocation
        comp = req.get("Business Component", "").strip()
        if comp:
            cypher_lines.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (c:Component {{name: "{clean_str(comp)}"}})\n'
                f'MERGE (r)-[:ALLOCATED_TO]->(c);'
            )

        # Variant links
        vars_str = req.get("Target Variant", "")
        for v in [x.strip() for x in vars_str.split(",") if x.strip()]:
            cypher_lines.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (v:Variant {{id: "{clean_str(v)}"}})\n'
                f'MERGE (r)-[:TARGETS_VARIANT]->(v);'
            )

        # OEM links
        oems_str = req.get("OEM Customization Flag", "")
        for o in [x.strip() for x in oems_str.split(",") if x.strip()]:
            cypher_lines.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (o:OEM {{name: "{clean_str(o)}"}})\n'
                f'MERGE (r)-[:APPLICABLE_TO_OEM]->(o);'
            )

        # Test Case links
        tcs_str = req.get("Test Cases Linked", "")
        for tc in [x.strip() for x in tcs_str.split(",") if x.strip()]:
            cypher_lines.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (t:TestCase {{id: "{clean_str(tc)}"}})\n'
                f'MERGE (r)-[:VERIFIED_BY]->(t);'
            )

    cypher_lines.append("\n// --- 7. Verification Summary Query ---")
    cypher_lines.append("MATCH (n) RETURN labels(n) as Label, count(*) as Count;")

    cypher_content = "\n".join(cypher_lines)
    with open(OUTPUT_CYPHER, "w", encoding="utf-8") as f:
        f.write(cypher_content)

    print(f"✅ Generated Cypher script: {OUTPUT_CYPHER} ({len(cypher_lines)} lines)")

    # Also build a JSON graph representation for offline local mock usage in neo4j_tools.py
    nodes = {}
    edges = []

    for req in req_rows:
        rid = req["Requirement ID"].strip()
        nodes[rid] = {
            "id": rid,
            "type": "Requirement",
            "title": req.get("Primary Text", "").strip(),
            "artifact_type": req.get("Artifact Type", "").strip(),
            "status": req.get("Status", "").strip(),
            "level": req.get("Level", "").strip(),
            "acceptance_criteria": req.get("Verification Criteria", "").strip(),
            "verification_level": req.get("Verification Level", "").strip(),
            "component": req.get("Business Component", "").strip(),
            "variants": [x.strip() for x in req.get("Target Variant", "").split(",") if x.strip()],
            "oems": [x.strip() for x in req.get("OEM Customization Flag", "").split(",") if x.strip()]
        }

        # Parent edge
        parent = req.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            edges.append({"from": rid, "rel": "CHILD_OF", "to": parent})

        comp = req.get("Business Component", "").strip()
        if comp:
            cid = f"COMP-{comp.replace(' ', '_').upper()}"
            if cid not in nodes:
                nodes[cid] = {"id": cid, "type": "Component", "name": comp}
            edges.append({"from": rid, "rel": "ALLOCATED_TO", "to": cid})

        for v in [x.strip() for x in req.get("Target Variant", "").split(",") if x.strip()]:
            if v not in nodes:
                nodes[v] = {"id": v, "type": "Variant", "name": v}
            edges.append({"from": rid, "rel": "TARGETS_VARIANT", "to": v})

        for tc in [x.strip() for x in req.get("Test Cases Linked", "").split(",") if x.strip()]:
            if tc not in nodes:
                nodes[tc] = {"id": tc, "type": "TestCase", "name": tc}
            edges.append({"from": rid, "rel": "VERIFIED_BY", "to": tc})

    seed_data = {"nodes": nodes, "edges": edges}
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2)

    print(f"✅ Generated JSON Graph Seed: {OUTPUT_JSON} with {len(nodes)} nodes and {len(edges)} edges!")


if __name__ == "__main__":
    main()
