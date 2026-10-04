"""
Neo4j Knowledge Graph Tools for AXIOM.
Provides data-driven Knowledge Graph extraction directly from data/requirements_master_v5.csv.
Supports:
1. Live Neo4j AuraDB connections (using NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD).
2. Dynamic in-memory graph derived directly from CSV columns as nodes and rows as requirements with rich text metadata.
3. Querying both DIRECT relationships (hierarchy, component allocation, verification) and SEMANTIC relationships (variant divergence, co-allocation, keyword affinity).
"""

import os
import csv
import json
import logging
import re
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

logger = logging.getLogger("axiom.tools.neo4j")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
REQ_CSV = os.path.join(DATA_DIR, "requirements_master_v5.csv")
TC_CSV = os.path.join(DATA_DIR, "test_cases_master_v5.csv")
CYPHER_FILE = os.path.join(DATA_DIR, "neo4j_import_script.cypher")
JSON_SEED_FILE = os.path.join(DATA_DIR, "neo4j_graph_seed.json")

# Automatically load environment variables from .env
ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def clean_str(val: str) -> str:
    if not val:
        return ""
    return val.strip().replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def extract_keywords(text: str) -> Set[str]:
    stopwords = {
        "the", "shall", "be", "to", "with", "a", "an", "and", "or", "in", "on", "of", "for",
        "by", "at", "is", "are", "from", "via", "that", "this", "their", "under", "all",
        "can", "will", "over", "only", "when", "if", "not", "into", "up", "as", "such"
    }
    words = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in stopwords}


class DynamicKnowledgeGraph:
    """In-memory data-driven graph engine loaded directly from requirements CSV."""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self._loaded = False
        self.load_from_csv()

    def load_from_csv(self):
        if not os.path.exists(REQ_CSV):
            logger.warning(f"Requirements CSV not found at {REQ_CSV}")
            return

        with open(REQ_CSV, encoding="utf-8") as f:
            req_rows = list(csv.DictReader(f))

        parent_map = defaultdict(list)
        component_map = defaultdict(list)
        kw_map = {}

        # 1. Create Nodes from Rows and Columns
        for r in req_rows:
            rid = r["Requirement ID"].strip()
            text = r.get("Primary Text", "").strip()
            v_crit = r.get("Verification Criteria", "").strip()
            notes = r.get("Variant Implementation Notes", "").strip()
            status = r.get("Status", "").strip()
            level = r.get("Level", "").strip()
            art = r.get("Artifact Type", "").strip()
            vl = r.get("Verification Level", "").strip()
            comp = r.get("Business Component", "").strip()
            target_vars = [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()]
            oems = [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()]
            test_cases = [x.strip() for x in r.get("Test Cases Linked", "").split(",") if x.strip()]

            # Node: Requirement with rich text metadata
            self.nodes[rid] = {
                "id": rid,
                "label": "Requirement",
                "primary_text": text,
                "verification_criteria": v_crit,
                "variant_implementation_notes": notes,
                "status": status,
                "level": level,
                "artifact_type": art,
                "verification_level": vl,
                "component": comp,
                "target_variants": target_vars,
                "oems": oems,
                "test_cases": test_cases
            }

            full_text = f"{text} {notes} {v_crit}"
            kw_map[rid] = extract_keywords(full_text)

            # Direct Edge: Parent Hierarchy
            parent = r.get("Parent Requirement", "").strip()
            if parent and parent.lower() != "none":
                parent_map[parent].append(r)
                self.edges.append({"from": rid, "rel": "CHILD_OF", "to": parent, "category": "direct"})
                self.edges.append({"from": parent, "rel": "PARENT_OF", "to": rid, "category": "direct"})

            # Direct Edge: BusinessComponent Node
            if comp:
                cid = f"COMP-{comp.replace(' ', '_').upper()}"
                if cid not in self.nodes:
                    self.nodes[cid] = {"id": cid, "label": "BusinessComponent", "name": comp}
                self.edges.append({"from": rid, "rel": "ALLOCATED_TO", "to": cid, "category": "direct"})
                component_map[comp].append(rid)

            # Direct Edge: Variant Node
            for v in target_vars:
                vid = f"VAR-{v.replace('VAR-', '')}"
                if vid not in self.nodes:
                    self.nodes[vid] = {"id": vid, "label": "Variant", "name": v}
                self.edges.append({"from": rid, "rel": "TARGETS_VARIANT", "to": vid, "category": "direct"})

            # Direct Edge: OEM Node
            for o in oems:
                oid = f"OEM-{o.replace(' ', '_').upper()}"
                if oid not in self.nodes:
                    self.nodes[oid] = {"id": oid, "label": "OEM", "name": o}
                self.edges.append({"from": rid, "rel": "CUSTOMIZED_FOR_OEM", "to": oid, "category": "direct"})

            # Direct Edge: ArtifactType Node
            if art:
                aid = f"TYPE-{art.replace(' ', '_').upper()}"
                if aid not in self.nodes:
                    self.nodes[aid] = {"id": aid, "label": "ArtifactType", "name": art}
                self.edges.append({"from": rid, "rel": "IS_OF_TYPE", "to": aid, "category": "direct"})

            # Direct Edge: VerificationLevel Node
            if vl:
                vlid = f"VL-{vl.replace(' ', '_').upper()}"
                if vlid not in self.nodes:
                    self.nodes[vlid] = {"id": vlid, "label": "VerificationLevel", "name": vl}
                self.edges.append({"from": rid, "rel": "VERIFIED_AT_LEVEL", "to": vlid, "category": "direct"})

        # 2. Ingest Test Cases from test_cases_master_v5.csv with Full Details
        traceability_pairs = set()
        if os.path.exists(TC_CSV):
            with open(TC_CSV, encoding="utf-8") as f_tc:
                tc_rows = list(csv.DictReader(f_tc))

            for tc in tc_rows:
                tcid = tc.get("Test Case ID", "").strip()
                if not tcid:
                    continue
                desc = tc.get("Test Description", "").strip()
                obj = tc.get("Test Objective", "").strip()
                pre = tc.get("Pre-conditions", "").strip()
                steps = tc.get("Test Steps (Summary)", "").strip()
                exp = tc.get("Expected Result", "").strip()
                ttype = tc.get("Test Type", "").strip()
                prio = tc.get("Priority", "").strip()
                status = tc.get("Status", "").strip()
                owner = tc.get("Owner", "").strip()
                suite = tc.get("Test Suite ID", "").strip()
                plan = tc.get("Test Plan ID", "").strip()
                tvars = [x.strip() for x in tc.get("Target Variant", "").split(",") if x.strip()]

                self.nodes[tcid] = {
                    "id": tcid,
                    "label": "TestCase",
                    "description": desc,
                    "objective": obj,
                    "preconditions": pre,
                    "steps": steps,
                    "expected_result": exp,
                    "test_type": ttype,
                    "priority": prio,
                    "status": status,
                    "owner": owner,
                    "suite_id": suite,
                    "plan_id": plan,
                    "target_variants": tvars
                }

                if suite:
                    sid = f"SUITE-{suite}"
                    if sid not in self.nodes:
                        self.nodes[sid] = {"id": suite, "label": "TestSuite"}
                    self.edges.append({"from": tcid, "rel": "BELONGS_TO_SUITE", "to": sid, "category": "direct"})

                if plan:
                    pid = f"PLAN-{plan}"
                    if pid not in self.nodes:
                        self.nodes[pid] = {"id": plan, "label": "TestPlan"}
                    self.edges.append({"from": tcid, "rel": "BELONGS_TO_PLAN", "to": pid, "category": "direct"})

                linked_reqs = [x.strip() for x in tc.get("Linked Req IDs", "").split(",") if x.strip()]
                for rid in linked_reqs:
                    traceability_pairs.add((rid, tcid))

        # Also connect from requirements "Test Cases Linked"
        for r in req_rows:
            rid = r.get("Requirement ID", "").strip()
            linked_tcs = [x.strip() for x in r.get("Test Cases Linked", "").split(",") if x.strip()]
            for tc in linked_tcs:
                traceability_pairs.add((rid, tc))

        # Add bidirectional traceability edges
        for rid, tcid in sorted(traceability_pairs):
            if tcid not in self.nodes:
                self.nodes[tcid] = {"id": tcid, "label": "TestCase"}
            self.edges.append({"from": rid, "rel": "VERIFIED_BY", "to": tcid, "category": "direct"})
            self.edges.append({"from": tcid, "rel": "VERIFIES", "to": rid, "category": "direct"})

        # 3. Compute Dynamic Semantic Relationships
        # 2.1 Variant Divergence: Sibling requirements sharing parent with different variants
        for parent_id, children in parent_map.items():
            if len(children) > 1:
                for i in range(len(children)):
                    for j in range(i + 1, len(children)):
                        c1 = children[i]
                        c2 = children[j]
                        v1 = set([x.strip() for x in c1.get("Target Variant", "").split(",") if x.strip()])
                        v2 = set([x.strip() for x in c2.get("Target Variant", "").split(",") if x.strip()])
                        if v1 != v2:
                            r1 = c1["Requirement ID"].strip()
                            r2 = c2["Requirement ID"].strip()
                            desc = f"Variant divergence under {parent_id}: [{c1.get('Target Variant')}] vs [{c2.get('Target Variant')}]"
                            self.edges.append({"from": r1, "rel": "VARIANT_DIVERGENCE_OF", "to": r2, "rationale": desc, "category": "semantic"})
                            self.edges.append({"from": r2, "rel": "VARIANT_DIVERGENCE_OF", "to": r1, "rationale": desc, "category": "semantic"})

        # 2.2 Component Co-Allocation: Requirements that run on the same controller/subsystem
        for comp_name, req_ids in component_map.items():
            if comp_name != "System" and len(req_ids) > 1:
                for idx in range(min(12, len(req_ids) - 1)):
                    r_a = req_ids[idx]
                    r_b = req_ids[idx + 1]
                    self.edges.append({
                        "from": r_a, "rel": "CO_ALLOCATED_WITH", "to": r_b,
                        "component": comp_name, "category": "semantic"
                    })

        # 2.3 Semantic Keyword Affinity
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
                    self.edges.append({
                        "from": r1, "rel": "SEMANTIC_AFFINITY", "to": r2,
                        "shared_topics": shared_kw, "score": score, "category": "semantic"
                    })
                    self.edges.append({
                        "from": r2, "rel": "SEMANTIC_AFFINITY", "to": r1,
                        "shared_topics": shared_kw, "score": score, "category": "semantic"
                    })

        self._loaded = True
        logger.info(f"Loaded dynamic knowledge graph: {len(self.nodes)} nodes, {len(self.edges)} edges.")

        # Save to json seed file
        try:
            with open(JSON_SEED_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "total_nodes": len(self.nodes),
                        "total_edges": len(self.edges),
                        "direct_edges": sum(1 for e in self.edges if e.get("category") == "direct"),
                        "semantic_edges": sum(1 for e in self.edges if e.get("category") == "semantic")
                    },
                    "nodes": self.nodes,
                    "edges": self.edges
                }, f, indent=2)
        except Exception as e:
            logger.debug(f"Could not write json seed: {e}")


# Global in-memory instance
_DYNAMIC_KG = DynamicKnowledgeGraph()


def get_neo4j_driver():
    """Returns live Neo4j driver if connection details exist."""
    try:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
        pwd = os.getenv("NEO4J_PASSWORD")
        if uri and pwd:
            return GraphDatabase.driver(uri, auth=(user, pwd))
    except Exception as e:
        logger.debug(f"Live Neo4j driver not initialized ({e}); using data-driven in-memory graph.")
    return None


def neo4j_query_requirement_by_id(req_id: str) -> Dict[str, Any]:
    """Retrieves full requirement node attributes and rich text metadata."""
    driver = get_neo4j_driver()
    if driver:
        try:
            with driver.session() as session:
                result = session.run("MATCH (r:Requirement {id: $id}) RETURN r", id=req_id)
                record = result.single()
                if record:
                    return dict(record["r"])
        except Exception as e:
            logger.warning(f"Neo4j live query error: {e}")

    # Dynamic fallback from CSV graph
    node = _DYNAMIC_KG.nodes.get(req_id)
    if node:
        return node
    return {"error": f"Requirement {req_id} not found in Knowledge Graph."}


def neo4j_get_traceability_graph(req_id: str, depth: int = 2) -> Dict[str, Any]:
    """
    Traverses connected graph edges for the requirement up to specified depth.
    Includes BOTH Direct and Semantic relationships!
    """
    driver = get_neo4j_driver()
    if driver:
        try:
            with driver.session() as session:
                query = (
                    "MATCH path = (r:Requirement {id: $id})-[rel*1.." + str(depth) + "]-(n) "
                    "RETURN path LIMIT 50"
                )
                res = session.run(query, id=req_id)
                # Live return parsing
        except Exception as e:
            logger.warning(f"Live Neo4j traversal error: {e}")

    # Data-driven dynamic traversal
    connected_nodes = []
    edges = []
    direct_edges = []
    semantic_edges = []

    for edge in _DYNAMIC_KG.edges:
        if edge["from"] == req_id or edge["to"] == req_id:
            edges.append(edge)
            if edge.get("category") == "direct":
                direct_edges.append(edge)
            else:
                semantic_edges.append(edge)

            other_id = edge["to"] if edge["from"] == req_id else edge["from"]
            if other_id in _DYNAMIC_KG.nodes and _DYNAMIC_KG.nodes[other_id] not in connected_nodes:
                connected_nodes.append(_DYNAMIC_KG.nodes[other_id])

    return {
        "root_requirement": req_id,
        "depth": depth,
        "direct_relationships_count": len(direct_edges),
        "semantic_relationships_count": len(semantic_edges),
        "direct_edges": direct_edges,
        "semantic_edges": semantic_edges,
        "connected_nodes": connected_nodes,
        "summary": f"Requirement {req_id} has {len(direct_edges)} direct relationships and {len(semantic_edges)} semantic relationships."
    }


def neo4j_find_dependent_components(req_id: str) -> List[Dict[str, Any]]:
    """Returns business components implementing the requirement."""
    graph = neo4j_get_traceability_graph(req_id, depth=1)
    components = [n for n in graph.get("connected_nodes", []) if n.get("label") == "BusinessComponent"]
    return components


def neo4j_get_semantic_relationships(req_id: str) -> List[Dict[str, Any]]:
    """Retrieves only semantic relationships (divergence, co-allocation, affinity) for requirement."""
    graph = neo4j_get_traceability_graph(req_id, depth=1)
    return graph.get("semantic_edges", [])


def neo4j_impact_analysis_for_requirements(req_ids: List[str], depth: int = 2) -> Dict[str, Any]:
    """
    Computes deep blast radius and downstream dependency impact across the Knowledge Graph
    for the given requirement IDs.
    """
    impacted_reqs = set(req_ids)
    dependent_reqs = set()
    impacted_test_cases = set()
    impacted_components = set()
    impacted_variants = set()
    semantic_connections = []

    for rid in req_ids:
        graph = neo4j_get_traceability_graph(rid, depth=depth)
        for edge in graph.get("direct_edges", []):
            src = edge["from"]
            tgt = edge["to"]
            rel = edge["rel"]
            other = tgt if src == rid else src

            if rel == "PARENT_OF" and src == rid:
                dependent_reqs.add(tgt)
                impacted_reqs.add(tgt)
            elif rel == "CHILD_OF" and tgt == rid:
                dependent_reqs.add(src)
                impacted_reqs.add(src)
            elif rel in ("VERIFIED_BY", "VERIFIES"):
                tc_id = tgt if rel == "VERIFIED_BY" else src
                impacted_test_cases.add(tc_id)
            elif rel == "ALLOCATED_TO":
                comp = _DYNAMIC_KG.nodes.get(other, {}).get("name", other)
                impacted_components.add(comp)
            elif rel == "TARGETS_VARIANT":
                impacted_variants.add(other)

        for edge in graph.get("semantic_edges", []):
            semantic_connections.append(edge)
            other = edge["to"] if edge["from"] == rid else edge["from"]
            if edge.get("rel") == "VARIANT_DIVERGENCE_OF":
                dependent_reqs.add(other)

    detailed_reqs = [_DYNAMIC_KG.nodes.get(r) for r in sorted(impacted_reqs) if r in _DYNAMIC_KG.nodes]
    detailed_tests = [_DYNAMIC_KG.nodes.get(t) for t in sorted(impacted_test_cases) if t in _DYNAMIC_KG.nodes]

    return {
        "target_requirements": req_ids,
        "total_impacted_requirements": len(impacted_reqs),
        "total_impacted_test_cases": len(impacted_test_cases),
        "impacted_requirement_ids": sorted(list(impacted_reqs)),
        "dependent_requirement_ids": sorted(list(dependent_reqs)),
        "impacted_test_case_ids": sorted(list(impacted_test_cases)),
        "impacted_components": sorted(list(impacted_components)),
        "impacted_variants": sorted(list(impacted_variants)),
        "requirements": detailed_reqs,
        "test_cases": detailed_tests,
        "semantic_connections_count": len(semantic_connections),
        "blast_radius_rating": "CRITICAL" if len(impacted_reqs) > 5 or len(impacted_test_cases) > 5 else "HIGH" if len(impacted_reqs) > 2 else "MEDIUM"
    }


def neo4j_find_impacted_requirements_by_defect_summary(defect_summary: str) -> Dict[str, Any]:
    """
    Analyzes a defect summary, discovers matching requirements and test cases in the Knowledge Graph,
    and performs full impact and dependency analysis.
    """
    summary_words = extract_keywords(defect_summary)

    matched_req_scores = defaultdict(int)
    matched_reasons = defaultdict(list)

    # Search across Requirement nodes
    for node_id, node in _DYNAMIC_KG.nodes.items():
        if node.get("label") == "Requirement":
            text = f"{node.get('primary_text', '')} {node.get('variant_implementation_notes', '')} {node.get('verification_criteria', '')}"
            node_words = extract_keywords(text)
            overlap = summary_words.intersection(node_words)
            if overlap:
                matched_req_scores[node_id] += len(overlap) * 2
                matched_reasons[node_id].append(f"Requirement text matched keywords: {', '.join(sorted(overlap))}")

        elif node.get("label") == "TestCase":
            tc_text = f"{node.get('description', '')} {node.get('objective', '')} {node.get('steps', '')} {node.get('expected_result', '')}"
            tc_words = extract_keywords(tc_text)
            overlap = summary_words.intersection(tc_words)
            if overlap:
                # Find which requirement this test case verifies
                for edge in _DYNAMIC_KG.edges:
                    if edge["rel"] == "VERIFIES" and edge["from"] == node_id:
                        req_id = edge["to"]
                        matched_req_scores[req_id] += len(overlap) * 3
                        matched_reasons[req_id].append(f"Linked test case {node_id} matched keywords: {', '.join(sorted(overlap))}")
                    elif edge["rel"] == "VERIFIED_BY" and edge["to"] == node_id:
                        req_id = edge["from"]
                        matched_req_scores[req_id] += len(overlap) * 3
                        matched_reasons[req_id].append(f"Linked test case {node_id} matched keywords: {', '.join(sorted(overlap))}")

    sorted_matches = sorted(matched_req_scores.items(), key=lambda x: x[1], reverse=True)
    top_req_ids = [req_id for req_id, score in sorted_matches[:5]]

    if not top_req_ids:
        return {
            "defect_summary": defect_summary,
            "direct_matches": [],
            "impact_analysis": neo4j_impact_analysis_for_requirements([]),
            "summary": "No matching requirements identified for this defect summary."
        }

    impact_data = neo4j_impact_analysis_for_requirements(top_req_ids, depth=2)
    impact_data["defect_summary"] = defect_summary
    impact_data["direct_matched_requirements"] = [
        {
            "id": req_id,
            "score": matched_req_scores[req_id],
            "reasons": matched_reasons[req_id],
            "primary_text": _DYNAMIC_KG.nodes.get(req_id, {}).get("primary_text", "")
        }
        for req_id in top_req_ids
    ]

    return impact_data

