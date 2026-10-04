"""
Data-Driven Knowledge Graph Builder for AXIOM.
Parses requirements CSV and dynamically constructs a graph where:
- Columns become dedicated Entity Nodes (BusinessComponent, Variant, OEM, ArtifactType, VerificationLevel, TestCase).
- Rows become Requirement nodes with rich text metadata (primary text, verification criteria, implementation notes).
- Direct relationships connect requirements to their column values and parent hierarchy.
- Semantic relationships are computed dynamically from data (variant divergence, component co-allocation, test co-verification, and domain keyword affinity).
Generates:
1. data/neo4j_import_script.cypher (Executable in Neo4j AuraDB / Browser)
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
OUTPUT_CYPHER = os.path.join(DATA_DIR, "neo4j_import_script.cypher")
OUTPUT_JSON = os.path.join(DATA_DIR, "neo4j_graph_seed.json")


def clean_str(val: str) -> str:
    """Escapes strings for Cypher queries."""
    if not val:
        return ""
    return val.strip().replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def extract_keywords(text: str) -> Set[str]:
    """Extracts domain keywords for semantic text affinity calculation."""
    stopwords = {
        "the", "shall", "be", "to", "with", "a", "an", "and", "or", "in", "on", "of", "for",
        "by", "at", "is", "are", "from", "via", "that", "this", "their", "under", "all",
        "can", "will", "over", "only", "when", "if", "not", "into", "up", "as", "such"
    }
    words = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in stopwords}


def build_data_driven_knowledge_graph():
    if not os.path.exists(REQ_CSV):
        raise FileNotFoundError(f"Requirements CSV not found at {REQ_CSV}")

    with open(REQ_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        req_rows = list(reader)

    # 1. Dynamically discover all unique entities across CSV columns
    artifact_types = set()
    verification_levels = set()
    business_components = set()
    variants = set()
    oems = set()
    test_cases = set()

    for row in req_rows:
        art = row.get("Artifact Type", "").strip()
        if art:
            artifact_types.add(art)

        vl = row.get("Verification Level", "").strip()
        if vl:
            verification_levels.add(vl)

        bc = row.get("Business Component", "").strip()
        if bc:
            business_components.add(bc)

        for v in [x.strip() for x in row.get("Target Variant", "").split(",") if x.strip()]:
            variants.add(v)

        for o in [x.strip() for x in row.get("OEM Customization Flag", "").split(",") if x.strip()]:
            oems.add(o)

        for tc in [x.strip() for x in row.get("Test Cases Linked", "").split(",") if x.strip()]:
            test_cases.add(tc)

    # 2. Build Cypher statements
    cypher = []
    cypher.append("// ===========================================================================")
    cypher.append("// AXIOM DATA-DRIVEN KNOWLEDGE GRAPH IMPORT SCRIPT")
    cypher.append("// Schema dynamically generated from CSV column headers & row values")
    cypher.append("// ===========================================================================\n")

    cypher.append("// --- 1. Indexes & Uniqueness Constraints ---")
    cypher.append("CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT component_name_unique IF NOT EXISTS FOR (c:BusinessComponent) REQUIRE c.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT variant_id_unique IF NOT EXISTS FOR (v:Variant) REQUIRE v.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT oem_name_unique IF NOT EXISTS FOR (o:OEM) REQUIRE o.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT artifact_type_unique IF NOT EXISTS FOR (a:ArtifactType) REQUIRE a.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT verification_level_unique IF NOT EXISTS FOR (vl:VerificationLevel) REQUIRE vl.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT test_case_id_unique IF NOT EXISTS FOR (t:TestCase) REQUIRE t.id IS UNIQUE;\n")

    # Column entity seeds
    cypher.append("// --- 2. Seed Column Value Nodes ---")
    for a in sorted(artifact_types):
        cypher.append(f'MERGE (:ArtifactType {{name: "{clean_str(a)}"}});')
    for vl in sorted(verification_levels):
        cypher.append(f'MERGE (:VerificationLevel {{name: "{clean_str(vl)}"}});')
    for bc in sorted(business_components):
        cypher.append(f'MERGE (:BusinessComponent {{name: "{clean_str(bc)}"}});')
    for v in sorted(variants):
        cypher.append(f'MERGE (:Variant {{id: "{clean_str(v)}"}});')
    for o in sorted(oems):
        cypher.append(f'MERGE (:OEM {{name: "{clean_str(o)}"}});')
    for tc in sorted(test_cases):
        cypher.append(f'MERGE (:TestCase {{id: "{clean_str(tc)}"}});')
    cypher.append("")

    # Requirement nodes with text metadata
    cypher.append("// --- 3. Seed Requirement Nodes with Rich Text Metadata ---")
    for r in req_rows:
        rid = clean_str(r.get("Requirement ID", ""))
        text = clean_str(r.get("Primary Text", ""))
        v_crit = clean_str(r.get("Verification Criteria", ""))
        notes = clean_str(r.get("Variant Implementation Notes", ""))
        status = clean_str(r.get("Status", ""))
        level = clean_str(r.get("Level", ""))

        cypher.append(
            f'MERGE (r:Requirement {{id: "{rid}"}}) '
            f'ON CREATE SET '
            f'r.primary_text = "{text}", '
            f'r.verification_criteria = "{v_crit}", '
            f'r.variant_implementation_notes = "{notes}", '
            f'r.status = "{status}", '
            f'r.level = "{level}";'
        )
    cypher.append("")

    # Direct Relationships (Requirement -> Column Nodes & Parent Hierarchy)
    cypher.append("// --- 4. DIRECT RELATIONSHIPS (Connecting Requirements to Column Nodes & Parent) ---")
    parent_map = defaultdict(list)
    component_map = defaultdict(list)
    kw_map = {}

    for r in req_rows:
        rid = clean_str(r.get("Requirement ID", ""))
        parent = r.get("Parent Requirement", "").strip()
        art = r.get("Artifact Type", "").strip()
        vl = r.get("Verification Level", "").strip()
        bc = r.get("Business Component", "").strip()

        # Text keywords for semantic search
        full_text = f"{r.get('Primary Text', '')} {r.get('Variant Implementation Notes', '')} {r.get('Verification Criteria', '')}"
        kw_map[rid] = extract_keywords(full_text)

        # Parent hierarchy
        if parent and parent.lower() != "none":
            parent_clean = clean_str(parent)
            parent_map[parent].append(r)
            cypher.append(
                f'MATCH (child:Requirement {{id: "{rid}"}}), (parent:Requirement {{id: "{parent_clean}"}})\n'
                f'MERGE (child)-[:CHILD_OF]->(parent)\n'
                f'MERGE (parent)-[:PARENT_OF]->(child);'
            )

        # Artifact Type
        if art:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (a:ArtifactType {{name: "{clean_str(art)}"}})\n'
                f'MERGE (r)-[:IS_OF_TYPE]->(a);'
            )

        # Verification Level
        if vl:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (v:VerificationLevel {{name: "{clean_str(vl)}"}})\n'
                f'MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);'
            )

        # Business Component
        if bc:
            component_map[bc].append(rid)
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (c:BusinessComponent {{name: "{clean_str(bc)}"}})\n'
                f'MERGE (r)-[:ALLOCATED_TO]->(c);'
            )

        # Variants
        for v in [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (v:Variant {{id: "{clean_str(v)}"}})\n'
                f'MERGE (r)-[:TARGETS_VARIANT]->(v);'
            )

        # OEMs
        for o in [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (o:OEM {{name: "{clean_str(o)}"}})\n'
                f'MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);'
            )

        # Test Cases
        for tc in [x.strip() for x in r.get("Test Cases Linked", "").split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{rid}"}}), (t:TestCase {{id: "{clean_str(tc)}"}})\n'
                f'MERGE (r)-[:VERIFIED_BY]->(t)\n'
                f'MERGE (t)-[:VERIFIES]->(r);'
            )
    cypher.append("")

    # =========================================================================
    # 5. SEMANTIC RELATIONSHIPS (Computed Dynamically from Data)
    # =========================================================================
    cypher.append("// ===========================================================================")
    cypher.append("// --- 5. SEMANTIC RELATIONSHIPS (Dynamically Inferred from Data Patterns) ---")
    cypher.append("// ===========================================================================\n")

    semantic_edges_data = []

    # 5.1 Variant Divergence: Siblings that share the same parent but target different variants
    cypher.append("// --- 5.1 Dynamic Variant Divergence (Sibling requirements targeting alternate variants) ---")
    for parent_id, children in parent_map.items():
        if len(children) > 1:
            for i in range(len(children)):
                for j in range(i + 1, len(children)):
                    c1 = children[i]
                    c2 = children[j]
                    v1 = set([x.strip() for x in c1.get("Target Variant", "").split(",") if x.strip()])
                    v2 = set([x.strip() for x in c2.get("Target Variant", "").split(",") if x.strip()])
                    # If variant sets differ, they represent variant divergence!
                    if v1 != v2:
                        id1 = clean_str(c1["Requirement ID"])
                        id2 = clean_str(c2["Requirement ID"])
                        diff_desc = f"Variant divergence under {parent_id}: [{c1.get('Target Variant')}] vs [{c2.get('Target Variant')}]"
                        cypher.append(
                            f'MATCH (r1:Requirement {{id: "{id1}"}}), (r2:Requirement {{id: "{id2}"}})\n'
                            f'MERGE (r1)-[:VARIANT_DIVERGENCE_OF {{parent: "{parent_id}", rationale: "{diff_desc}"}}]->(r2)\n'
                            f'MERGE (r2)-[:VARIANT_DIVERGENCE_OF {{parent: "{parent_id}", rationale: "{diff_desc}"}}]->(r1);'
                        )
                        semantic_edges_data.append({
                            "from": id1, "to": id2, "rel": "VARIANT_DIVERGENCE_OF",
                            "rationale": diff_desc, "category": "semantic"
                        })
    cypher.append("")

    # 5.2 Component Co-Allocation: Requirements that share the same physical controller or module
    cypher.append("// --- 5.2 Dynamic Component Co-Allocation (Execution coupling on same component) ---")
    for comp_name, req_ids in component_map.items():
        if comp_name != "System" and len(req_ids) > 1:
            # Connect consecutive requirements in the same component
            for idx in range(min(15, len(req_ids) - 1)):
                r_a = req_ids[idx]
                r_b = req_ids[idx + 1]
                rationale = f"Co-allocated on business component: {comp_name}"
                cypher.append(
                    f'MATCH (r1:Requirement {{id: "{r_a}"}}), (r2:Requirement {{id: "{r_b}"}})\n'
                    f'MERGE (r1)-[:CO_ALLOCATED_WITH {{component: "{clean_str(comp_name)}"}}]->(r2);'
                )
                semantic_edges_data.append({
                    "from": r_a, "to": r_b, "rel": "CO_ALLOCATED_WITH",
                    "component": comp_name, "category": "semantic"
                })
    cypher.append("")

    # 5.3 Semantic Domain Keyword Affinity: Dynamically computed Jaccard text overlap
    cypher.append("// --- 5.3 Dynamic Semantic Keyword Affinity (Topical correlation across text metadata) ---")
    req_ids_list = list(kw_map.keys())
    for i in range(len(req_ids_list)):
        for j in range(i + 1, len(req_ids_list)):
            r1 = req_ids_list[i]
            r2 = req_ids_list[j]
            k1 = kw_map[r1]
            k2 = kw_map[r2]
            intersection = k1.intersection(k2)
            # Domain-critical topic overlap (e.g. proximity, offline, encryption, telemetry, enrollment, revocation)
            critical_topics = {"proximity", "unlock", "lock", "ble", "uwb", "encryption", "offline", "grace", "revocation", "telemetry", "biometric", "valet", "speed", "jwt", "tls"}
            matched_critical = intersection.intersection(critical_topics)

            if len(matched_critical) >= 2 or (len(intersection) >= 4 and len(matched_critical) >= 1):
                shared_kw_str = ", ".join(sorted(matched_critical if matched_critical else list(intersection)[:3]))
                score = round(len(intersection) / max(1, len(k1.union(k2))), 3)
                cypher.append(
                    f'MATCH (r1:Requirement {{id: "{r1}"}}), (r2:Requirement {{id: "{r2}"}})\n'
                    f'MERGE (r1)-[:SEMANTIC_AFFINITY {{shared_topics: "{shared_kw_str}", score: {score}}}]->(r2)\n'
                    f'MERGE (r2)-[:SEMANTIC_AFFINITY {{shared_topics: "{shared_kw_str}", score: {score}}}]->(r1);'
                )
                semantic_edges_data.append({
                    "from": r1, "to": r2, "rel": "SEMANTIC_AFFINITY",
                    "shared_topics": shared_kw_str, "score": score, "category": "semantic"
                })
    cypher.append("")

    # 6. Verification Summary Query
    cypher.append("// --- 6. Verification Summary Query ---")
    cypher.append("MATCH (n) RETURN labels(n) as EntityType, count(*) as NodeCount ORDER BY NodeCount DESC;")
    cypher.append("MATCH ()-[r]->() RETURN type(r) as RelationshipType, count(*) as EdgeCount ORDER BY EdgeCount DESC;")

    # Write Cypher File
    cypher_text = "\n".join(cypher)
    with open(OUTPUT_CYPHER, "w", encoding="utf-8") as f:
        f.write(cypher_text)

    # 7. Write complete JSON seed data for in-memory neo4j_tools.py execution
    nodes_json = {}
    edges_json = []

    # Requirements
    for r in req_rows:
        rid = r["Requirement ID"].strip()
        nodes_json[rid] = {
            "id": rid,
            "type": "Requirement",
            "primary_text": r.get("Primary Text", "").strip(),
            "verification_criteria": r.get("Verification Criteria", "").strip(),
            "variant_implementation_notes": r.get("Variant Implementation Notes", "").strip(),
            "status": r.get("Status", "").strip(),
            "level": r.get("Level", "").strip(),
            "artifact_type": r.get("Artifact Type", "").strip(),
            "verification_level": r.get("Verification Level", "").strip(),
            "component": r.get("Business Component", "").strip(),
            "variants": [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()],
            "oems": [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()],
            "test_cases": [x.strip() for x in r.get("Test Cases Linked", "").split(",") if x.strip()]
        }

        # Parent hierarchy direct edge
        parent = r.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            edges_json.append({"from": rid, "rel": "CHILD_OF", "to": parent, "category": "direct"})
            edges_json.append({"from": parent, "rel": "PARENT_OF", "to": rid, "category": "direct"})

        # Component allocation direct edge
        comp = r.get("Business Component", "").strip()
        if comp:
            cid = f"COMP-{comp.replace(' ', '_').upper()}"
            if cid not in nodes_json:
                nodes_json[cid] = {"id": cid, "type": "BusinessComponent", "name": comp}
            edges_json.append({"from": rid, "rel": "ALLOCATED_TO", "to": cid, "category": "direct"})

        # Variant direct edge
        for v in [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()]:
            if v not in nodes_json:
                nodes_json[v] = {"id": v, "type": "Variant", "id_name": v}
            edges_json.append({"from": rid, "rel": "TARGETS_VARIANT", "to": v, "category": "direct"})

        # OEM direct edge
        for o in [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()]:
            oid = f"OEM-{o.replace(' ', '_').upper()}"
            if oid not in nodes_json:
                nodes_json[oid] = {"id": oid, "type": "OEM", "name": o}
            edges_json.append({"from": rid, "rel": "CUSTOMIZED_FOR_OEM", "to": oid, "category": "direct"})

        # Test case direct edge
        for tc in [x.strip() for x in r.get("Test Cases Linked", "").split(",") if x.strip()]:
            if tc not in nodes_json:
                nodes_json[tc] = {"id": tc, "type": "TestCase", "id_name": tc}
            edges_json.append({"from": rid, "rel": "VERIFIED_BY", "to": tc, "category": "direct"})
            edges_json.append({"from": tc, "rel": "VERIFIES", "to": rid, "category": "direct"})

        # Artifact type direct edge
        art = r.get("Artifact Type", "").strip()
        if art:
            aid = f"TYPE-{art.replace(' ', '_').upper()}"
            if aid not in nodes_json:
                nodes_json[aid] = {"id": aid, "type": "ArtifactType", "name": art}
            edges_json.append({"from": rid, "rel": "IS_OF_TYPE", "to": aid, "category": "direct"})

        # Verification level direct edge
        vl = r.get("Verification Level", "").strip()
        if vl:
            vlid = f"VL-{vl.replace(' ', '_').upper()}"
            if vlid not in nodes_json:
                nodes_json[vlid] = {"id": vlid, "type": "VerificationLevel", "name": vl}
            edges_json.append({"from": rid, "rel": "VERIFIED_AT_LEVEL", "to": vlid, "category": "direct"})

    # Add all dynamically computed semantic edges
    edges_json.extend(semantic_edges_data)

    seed_dataset = {
        "metadata": {
            "title": "AXIOM Dynamic Knowledge Graph (E-Key 2W Digital Key Platform)",
            "source_csv": "data/requirements_master_v5.csv",
            "total_nodes": len(nodes_json),
            "total_edges": len(edges_json),
            "direct_relationships_count": sum(1 for e in edges_json if e.get("category") == "direct"),
            "semantic_relationships_count": sum(1 for e in edges_json if e.get("category") == "semantic")
        },
        "nodes": nodes_json,
        "edges": edges_json
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(seed_dataset, f, indent=2)

    return seed_dataset


if __name__ == "__main__":
    result = build_data_driven_knowledge_graph()
    meta = result["metadata"]
    print(f"Knowledge Graph Created Successfully!")
    print(f"- Total Nodes: {meta['total_nodes']}")
    print(f"- Total Edges: {meta['total_edges']}")
    print(f"  * Direct Relationships: {meta['direct_relationships_count']}")
    print(f"  * Semantic Relationships: {meta['semantic_relationships_count']}")
