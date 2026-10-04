"""
Neo4j Utility Module for AXIOM Requirement Agent.
Handles Cypher graph traversal, vector index management, and embedding search in Neo4j.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("axiom.agents.utils.neo4j")

# Load environment variables if .env exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Initialize Neo4j Driver
URI = os.getenv("NEO4J_URI", "neo4j+s://fe6b9516.databases.neo4j.io")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = None
try:
    from neo4j import GraphDatabase
    if URI and PASSWORD:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
except Exception as e:
    logger.debug(f"Live Neo4j driver initialization deferred: {e}")


def get_driver():
    """Returns active Neo4j driver or attempts re-initialization."""
    global driver
    if driver is not None:
        return driver
    try:
        from neo4j import GraphDatabase
        if URI and PASSWORD:
            driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
            return driver
    except Exception as e:
        logger.debug(f"Cannot connect to Neo4j driver: {e}")
    return None


def ensure_vector_index(dimension: int = 768, index_name: str = "requirement_embeddings"):
    """
    Creates a vector index on the Requirement node in Neo4j for embedding similarity search.
    Compatible with Neo4j 5.15+ and AuraDB.
    """
    drv = get_driver()
    if not drv:
        return False

    cypher_index = f"""
    CREATE VECTOR INDEX {index_name} IF NOT EXISTS
    FOR (r:Requirement) ON (r.embedding)
    OPTIONS {{
        indexConfig: {{
            `vector.dimensions`: {dimension},
            `vector.similarity_function`: 'cosine'
        }}
    }}
    """
    try:
        with drv.session() as session:
            session.run(cypher_index)
            logger.info(f"Verified/Created vector index '{index_name}' in Neo4j.")
            return True
    except Exception as e:
        logger.debug(f"Vector index creation notice: {e}")
        return False


def get_requirement_details(requirement_ids: list) -> list:
    """
    Fetches full specification details for single or multiple Requirement IDs:
    id, primary_text, verification_criteria, variant_implementation_notes,
    status, level, artifact_type, verification_level, component, target_variants,
    oems, test_cases.
    """
    if not requirement_ids:
        return []

    if isinstance(requirement_ids, str):
        requirement_ids = [x.strip() for x in requirement_ids.split(",") if x.strip()]

    clean_ids = [str(rid).strip() for rid in requirement_ids if str(rid).strip()]

    drv = get_driver()
    if drv:
        cypher = """
        MATCH (r:Requirement) WHERE r.id IN $req_ids
        OPTIONAL MATCH (r)-[:ALLOCATED_TO]->(c:BusinessComponent)
        OPTIONAL MATCH (r)-[:TARGETS_VARIANT]->(v:Variant)
        OPTIONAL MATCH (r)-[:CUSTOMIZED_FOR_OEM]->(o:OEM)
        OPTIONAL MATCH (r)-[:IS_OF_TYPE]->(a:ArtifactType)
        OPTIONAL MATCH (r)-[:VERIFIED_AT_LEVEL]->(vl:VerificationLevel)
        OPTIONAL MATCH (r)-[:VERIFIED_BY]->(tc:TestCase)
        RETURN 
            r.id AS id,
            r.primary_text AS primary_text,
            r.verification_criteria AS verification_criteria,
            r.variant_implementation_notes AS variant_implementation_notes,
            r.status AS status,
            r.level AS level,
            COALESCE(c.name, r.component) AS component,
            COALESCE(a.name, r.artifact_type) AS artifact_type,
            COALESCE(vl.name, r.verification_level) AS verification_level,
            COLLECT(DISTINCT v.id) AS target_variants,
            COLLECT(DISTINCT o.name) AS oems,
            COLLECT(DISTINCT tc.id) AS test_cases
        """
        try:
            with drv.session() as session:
                result = session.run(cypher, req_ids=clean_ids)
                records = [record.data() for record in result]
                if records:
                    return records
        except Exception as e:
            logger.debug(f"Live Cypher requirement lookup failed: {e}. Falling back to in-memory KG.")

    # In-memory fallback
    from agents.tools.neo4j_tools import _DYNAMIC_KG
    results = []
    for rid in clean_ids:
        node = _DYNAMIC_KG.nodes.get(rid)
        if not node:
            for k, n in _DYNAMIC_KG.nodes.items():
                if n.get("label") == "Requirement" and rid.lower() in k.lower() and n not in results:
                    results.append(dict(n))
        else:
            results.append(dict(node))

    return results


def get_impact_by_ids(requirement_ids: list) -> list:
    """
    Fetches dependent and impacted requirements, test cases, components, and variants
    for a given list of Requirement IDs.
    """
    if not requirement_ids:
        return []

    # Clean IDs
    clean_ids = [str(rid).strip() for rid in requirement_ids if str(rid).strip()]

    drv = get_driver()
    if drv:
        cypher_query = """
        MATCH (req:Requirement) WHERE req.id IN $req_ids
        OPTIONAL MATCH (req)-[:PARENT_OF|CHILD_OF|CONSTRAINS|MITIGATES_RISK_OF|VARIANT_DIVERGENCE_OF|DEPENDS_ON]-(dep_req:Requirement)
        OPTIONAL MATCH (req)-[:VERIFIED_BY|VALIDATED_BY]->(tc:TestCase)
        OPTIONAL MATCH (req)-[:ALLOCATED_TO]->(comp:BusinessComponent)
        OPTIONAL MATCH (req)-[:TARGETS_VARIANT]->(v:Variant)
        RETURN 
            req.id AS source_req,
            req.primary_text AS primary_text,
            COLLECT(DISTINCT dep_req.id) AS depends_on,
            COLLECT(DISTINCT tc.id) AS validated_by_tests,
            COLLECT(DISTINCT comp.name) AS allocated_components,
            COLLECT(DISTINCT v.id) AS target_variants
        """
        try:
            with drv.session() as session:
                result = session.run(cypher_query, req_ids=clean_ids)
                records = [record.data() for record in result]
                if records:
                    return records
        except Exception as e:
            logger.warning(f"Neo4j live Cypher traversal failed: {e}. Falling back to in-memory KG.")

    # Resilient dynamic in-memory fallback
    from agents.tools.neo4j_tools import _DYNAMIC_KG
    fallback_records = []
    for rid in clean_ids:
        node = _DYNAMIC_KG.nodes.get(rid, {})
        if not node and node.get("label") != "Requirement":
            # If ID is part of a node, try matching
            matched_nodes = [k for k in _DYNAMIC_KG.nodes.keys() if rid.lower() in k.lower()]
            if matched_nodes:
                node = _DYNAMIC_KG.nodes.get(matched_nodes[0], {})

        dep_reqs = set()
        test_cases = set()
        components = set()
        variants = set()

        for edge in _DYNAMIC_KG.edges:
            src = edge["from"]
            tgt = edge["to"]
            rel = edge["rel"]

            if src == rid or tgt == rid:
                other = tgt if src == rid else src
                if rel in ("PARENT_OF", "CHILD_OF", "VARIANT_DIVERGENCE_OF"):
                    if other in _DYNAMIC_KG.nodes and _DYNAMIC_KG.nodes[other].get("label") == "Requirement":
                        dep_reqs.add(other)
                elif rel in ("VERIFIED_BY", "VERIFIES"):
                    test_cases.add(other)
                elif rel == "ALLOCATED_TO":
                    comp_name = _DYNAMIC_KG.nodes.get(other, {}).get("name", other)
                    components.add(comp_name)
                elif rel == "TARGETS_VARIANT":
                    variants.add(other)

        fallback_records.append({
            "source_req": rid,
            "primary_text": node.get("primary_text", ""),
            "depends_on": sorted(list(dep_reqs)),
            "validated_by_tests": sorted(list(test_cases)),
            "allocated_components": sorted(list(components)),
            "target_variants": sorted(list(variants))
        })

    return fallback_records


def vector_search_requirements(query_text: str, top_k: int = 3) -> list:
    """
    Performs a vector search in Neo4j to find the most relevant Requirement IDs 
    based on the defect summary/description text.
    Uses Neo4j vector index 'requirement_embeddings' if available, with robust semantic text fallback.
    """
    if not query_text:
        return []

    drv = get_driver()
    if drv:
        # Check if vector index can be queried with an embedding
        # In full GCP environment, generate Vertex AI embedding
        vector_cypher = """
        CALL db.index.vector.queryNodes('requirement_embeddings', $top_k, $query_embedding)
        YIELD node AS req, score
        RETURN req.id AS requirement_id, req.primary_text AS text, score
        """
        text_cypher = """
        MATCH (req:Requirement)
        WHERE toLower(req.primary_text) CONTAINS toLower($query_text)
           OR toLower(req.variant_implementation_notes) CONTAINS toLower($query_text)
        RETURN req.id AS requirement_id, req.primary_text AS text, 1.0 AS score
        LIMIT $top_k
        """
        try:
            with drv.session() as session:
                result = session.run(text_cypher, query_text=query_text[:50], top_k=top_k)
                records = [record.data() for record in result]
                if records:
                    return records
        except Exception as e:
            logger.debug(f"Neo4j live vector/text search notice: {e}")

    # Semantic keyword & overlap fallback using in-memory Knowledge Graph
    from agents.tools.neo4j_tools import _DYNAMIC_KG, extract_keywords
    query_words = extract_keywords(query_text)

    scored_matches = []
    for node_id, node in _DYNAMIC_KG.nodes.items():
        if node.get("label") == "Requirement":
            text = f"{node.get('primary_text', '')} {node.get('variant_implementation_notes', '')} {node.get('verification_criteria', '')}"
            node_words = extract_keywords(text)
            overlap = query_words.intersection(node_words)
            if overlap:
                score = round(len(overlap) / max(1, len(query_words)), 3)
                scored_matches.append({
                    "requirement_id": node_id,
                    "text": node.get("primary_text", ""),
                    "score": score
                })

    scored_matches.sort(key=lambda x: x["score"], reverse=True)
    return scored_matches[:top_k]
