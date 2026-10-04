"""
Builds the complete AXIOM Knowledge Graph with both:
1. Direct Relationships (Structural, Decomposition, Allocation, Verification)
2. Semantic Relationships (Cross-Requirement Functional, Safety, Regulatory, Conflict & Ripple Links)
Generates:
- data/neo4j_import_script.cypher (for direct AuraDB / Neo4j execution)
- data/neo4j_graph_seed.json (for offline in-memory execution in neo4j_tools.py)
"""

import csv
import json
import os
import sys

# Configure UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
REQ_CSV = os.path.join(DATA_DIR, "requirements_master_v5.csv")
TC_CSV = os.path.join(DATA_DIR, "test_cases_master_v5.csv")
OUTPUT_CYPHER = os.path.join(DATA_DIR, "neo4j_import_script.cypher")
OUTPUT_JSON = os.path.join(DATA_DIR, "neo4j_graph_seed.json")


def escape_str(s: str) -> str:
    if not s:
        return ""
    return s.strip().replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def build_graph():
    print("Parsing CSV data...")
    with open(REQ_CSV, encoding="utf-8") as f:
        req_rows = list(csv.DictReader(f))

    with open(TC_CSV, encoding="utf-8") as f:
        tc_rows = list(csv.DictReader(f))

    cypher = []
    cypher.append("// ===========================================================================")
    cypher.append("// AXIOM KNOWLEDGE GRAPH: E-Key 2W Digital Key Platform")
    cypher.append("// Includes both DIRECT relationships (decomposition, allocation, verification)")
    cypher.append("// and SEMANTIC relationships (functional dependency, risk mitigation, alternatives)")
    cypher.append("// ===========================================================================\n")

    # 1. Constraints & Indexes
    cypher.append("// --- 1. Indexes & Uniqueness Constraints ---")
    cypher.append("CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT test_case_id_unique IF NOT EXISTS FOR (t:TestCase) REQUIRE t.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT component_name_unique IF NOT EXISTS FOR (c:Component) REQUIRE c.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT variant_id_unique IF NOT EXISTS FOR (v:Variant) REQUIRE v.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT oem_name_unique IF NOT EXISTS FOR (o:OEM) REQUIRE o.name IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT feature_id_unique IF NOT EXISTS FOR (f:Feature) REQUIRE f.id IS UNIQUE;")
    cypher.append("CREATE CONSTRAINT compliance_id_unique IF NOT EXISTS FOR (cp:ComplianceStandard) REQUIRE cp.id IS UNIQUE;\n")

    # Extract distinct sets
    components = set()
    variants = set()
    oems = set()

    for r in req_rows:
        c = r.get("Business Component", "").strip()
        if c:
            components.add(c)
        for v in [x.strip() for x in r.get("Target Variant", "").split(",") if x.strip()]:
            variants.add(v)
        for o in [x.strip() for x in r.get("OEM Customization Flag", "").split(",") if x.strip()]:
            oems.add(o)

    # 2. Components
    cypher.append("// --- 2. Seed Component Nodes ---")
    for c in sorted(components):
        cypher.append(f'MERGE (:Component {{name: "{escape_str(c)}"}});')
    cypher.append("")

    # 3. Variants
    cypher.append("// --- 3. Seed Variant Nodes ---")
    for v in sorted(variants):
        cypher.append(f'MERGE (:Variant {{id: "{escape_str(v)}"}});')
    cypher.append("")

    # 4. OEMs
    cypher.append("// --- 4. Seed OEM Nodes ---")
    for o in sorted(oems):
        cypher.append(f'MERGE (:OEM {{name: "{escape_str(o)}"}});')
    cypher.append("")

    # 5. Compliance Standards
    compliance_standards = [
        {"id": "COMP-GDPR-ART17", "name": "GDPR Article 17", "description": "Right to be Forgotten (Data Erasure within 30 days)"},
        {"id": "COMP-GDPR-ART20", "name": "GDPR Article 20", "description": "Right to Data Portability (JSON Machine Readable)"},
        {"id": "COMP-CCPA-1798", "name": "CCPA Title 1.81.5", "description": "California Consumer Privacy Act Opt-Out of Sale"},
        {"id": "COMP-WCAG-21AA", "name": "WCAG 2.1 Level AA", "description": "Web Content Accessibility Guidelines"},
        {"id": "COMP-ISO-8601", "name": "ISO 8601", "description": "International Standard Date and Time Representation"},
        {"id": "COMP-TLS-13", "name": "RFC 8446 (TLS 1.3)", "description": "Transport Layer Security Encryption in Transit"},
        {"id": "COMP-NIST-AES256", "name": "NIST FIPS 197", "description": "Advanced Encryption Standard 256-bit at Rest"}
    ]
    cypher.append("// --- 5. Seed Compliance & Regulatory Nodes ---")
    for cp in compliance_standards:
        cypher.append(f'MERGE (:ComplianceStandard {{id: "{cp["id"]}", name: "{cp["name"]}", description: "{cp["description"]}"}});')
    cypher.append("")

    # 6. Features
    features = [
        {"id": "FEAT-01", "name": "Digital Key Enrollment", "desc": "BLE pairing and secure cloud key provisioning"},
        {"id": "FEAT-02", "name": "Passive Unlock and Lock", "desc": "Hands-free proximity detection and vehicle access"},
        {"id": "FEAT-03", "name": "Ride Authorization", "desc": "Cryptographic authentication before motor/ignition enable"},
        {"id": "FEAT-04", "name": "Key Sharing", "desc": "Delegated temporary access with constraints"},
        {"id": "FEAT-05", "name": "Key Revocation", "desc": "Immediate CRL propagation and revocation"},
        {"id": "FEAT-06", "name": "Rider Profiles", "desc": "Time-window and shift-based permission customization"},
        {"id": "FEAT-07", "name": "Valet & Service Mode", "desc": "Restricted performance and trunk lock service key"},
        {"id": "FEAT-08", "name": "Security & Event Monitoring", "desc": "Immutable audit trails and SIEM event streaming"},
        {"id": "FEAT-09", "name": "Vehicle Status & Telemetry", "desc": "Periodic REST and real-time WebSocket sync"},
        {"id": "FEAT-10", "name": "Offline Grace Mode", "desc": "72-hour bounded offline operational resilience"},
        {"id": "FEAT-PLAT-SEC", "name": "Platform Security", "desc": "TLS 1.3, AES-256, centralized secrets and container scan"},
        {"id": "FEAT-GLOB-COMP", "name": "Global Compliance", "desc": "GDPR, CCPA, and data residency"},
        {"id": "FEAT-PLAT-REL", "name": "Reliability & Scalability", "desc": "Rate limiting, read replicas, multi-AZ, and CDN"},
        {"id": "FEAT-PLAT-OBS", "name": "Observability & Lifecycle", "desc": "Centralized logs, automated alerts, tracing, and data aging"},
        {"id": "FEAT-GLOB-LOC", "name": "Global Localization", "desc": "UTC timestamps, ISO 8601, and 15-language i18n"}
    ]
    cypher.append("// --- 6. Seed Feature Nodes ---")
    for f_item in features:
        cypher.append(f'MERGE (:Feature {{id: "{f_item["id"]}", name: "{f_item["name"]}", description: "{f_item["desc"]}"}});')
    cypher.append("")

    # 7. Test Cases
    cypher.append("// --- 7. Seed TestCase Nodes ---")
    for tc in tc_rows:
        tc_id = escape_str(tc.get("Test Case ID", ""))
        desc = escape_str(tc.get("Test Description", ""))
        t_type = escape_str(tc.get("Test Type", ""))
        prio = escape_str(tc.get("Priority", ""))
        status = escape_str(tc.get("Status", ""))
        owner = escape_str(tc.get("Owner", ""))
        suite = escape_str(tc.get("Test Suite ID", ""))
        plan = escape_str(tc.get("Test Plan ID", ""))

        cypher.append(
            f'MERGE (t:TestCase {{id: "{tc_id}"}}) '
            f'ON CREATE SET t.description = "{desc}", t.type = "{t_type}", '
            f't.priority = "{prio}", t.status = "{status}", t.owner = "{owner}", '
            f't.suite_id = "{suite}", t.plan_id = "{plan}";'
        )
    cypher.append("")

    # 8. Requirements & Direct Relationships
    cypher.append("// --- 8. Seed Requirement Nodes & Direct Relationships ---")
    for req in req_rows:
        req_id = escape_str(req.get("Requirement ID", ""))
        art_type = escape_str(req.get("Artifact Type", ""))
        text = escape_str(req.get("Primary Text", ""))
        v_crit = escape_str(req.get("Verification Criteria", ""))
        v_lvl = escape_str(req.get("Verification Level", ""))
        status = escape_str(req.get("Status", ""))
        level = escape_str(req.get("Level", ""))
        notes = escape_str(req.get("Variant Implementation Notes", ""))

        cypher.append(
            f'MERGE (r:Requirement {{id: "{req_id}"}}) '
            f'ON CREATE SET r.text = "{text}", r.artifact_type = "{art_type}", '
            f'r.verification_criteria = "{v_crit}", r.verification_level = "{v_lvl}", '
            f'r.status = "{status}", r.level = "{level}", r.notes = "{notes}";'
        )

        # Hierarchy: CHILD_OF and PARENT_OF
        parent = req.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            cypher.append(
                f'MATCH (child:Requirement {{id: "{req_id}"}}), (parent:Requirement {{id: "{escape_str(parent)}"}})\n'
                f'MERGE (child)-[:CHILD_OF]->(parent)\n'
                f'MERGE (parent)-[:PARENT_OF]->(child);'
            )

        # Component allocation
        comp = req.get("Business Component", "").strip()
        if comp:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (c:Component {{name: "{escape_str(comp)}"}})\n'
                f'MERGE (r)-[:ALLOCATED_TO]->(c);'
            )

        # Variant links
        vars_str = req.get("Target Variant", "")
        for v in [x.strip() for x in vars_str.split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (v:Variant {{id: "{escape_str(v)}"}})\n'
                f'MERGE (r)-[:TARGETS_VARIANT]->(v);'
            )

        # OEM links
        oems_str = req.get("OEM Customization Flag", "")
        for o in [x.strip() for x in oems_str.split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (o:OEM {{name: "{escape_str(o)}"}})\n'
                f'MERGE (r)-[:APPLICABLE_TO_OEM]->(o);'
            )

        # Verification: VERIFIED_BY and VERIFIES
        tcs_str = req.get("Test Cases Linked", "")
        for tc in [x.strip() for x in tcs_str.split(",") if x.strip()]:
            cypher.append(
                f'MATCH (r:Requirement {{id: "{req_id}"}}), (t:TestCase {{id: "{escape_str(tc)}"}})\n'
                f'MERGE (r)-[:VERIFIED_BY]->(t)\n'
                f'MERGE (t)-[:VERIFIES]->(r);'
            )
    cypher.append("")

    # 9. Map Features to Requirements (Direct Relationship)
    cypher.append("// --- 9. Feature Inclusion Relationships ---")
    feature_mappings = [
        ("FEAT-01", ["REQ-L2-001", "REQ-L3-001", "REQ-L4-001", "REQ-L5-001", "REQ-L5-002", "REQ-L5-003", "REQ-L5-004"]),
        ("FEAT-02", ["REQ-L2-002", "REQ-L3-002", "REQ-L4-002", "REQ-L5-003", "REQ-L5-004", "REQ-L5-005", "REQ-L5-006"]),
        ("FEAT-03", ["REQ-L2-003", "REQ-L3-003", "REQ-L4-003", "REQ-L5-007", "REQ-L5-008"]),
        ("FEAT-04", ["REQ-L2-004", "REQ-L3-004", "REQ-L5-009", "REQ-L5-010", "REQ-L5-011"]),
        ("FEAT-05", ["REQ-L2-005", "REQ-L3-005", "REQ-L4-005", "REQ-L5-012"]),
        ("FEAT-06", ["REQ-L2-006", "REQ-L3-006", "REQ-L5-013", "REQ-L5-014"]),
        ("FEAT-07", ["REQ-L2-007", "REQ-L3-007", "REQ-L5-015", "REQ-L5-016"]),
        ("FEAT-08", ["REQ-L2-008", "REQ-L3-008", "REQ-L4-006", "REQ-L4-007", "REQ-L5-017"]),
        ("FEAT-09", ["REQ-L2-009", "REQ-L3-009", "REQ-L5-018", "REQ-L5-019", "REQ-L5-020"]),
        ("FEAT-10", ["REQ-L2-010", "REQ-L3-010", "REQ-L4-009", "REQ-L5-021"]),
        ("FEAT-PLAT-SEC", ["REQ-L3-037", "REQ-L3-038", "REQ-L5-037", "REQ-L4-037"]),
        ("FEAT-GLOB-COMP", ["REQ-L3-039", "REQ-L3-040", "REQ-L5-038", "REQ-L5-039", "REQ-L5-040"]),
        ("FEAT-PLAT-REL", ["REQ-L4-038", "REQ-L4-039", "REQ-L5-041", "REQ-L4-040", "REQ-L4-041", "REQ-L3-041"]),
        ("FEAT-PLAT-OBS", ["REQ-L5-042", "REQ-L4-042", "REQ-L5-043", "REQ-L5-044"]),
        ("FEAT-GLOB-LOC", ["REQ-L3-042", "REQ-L5-045", "REQ-L5-046", "REQ-L3-043"])
    ]
    for fid, req_list in feature_mappings:
        for rid in req_list:
            cypher.append(
                f'MATCH (f:Feature {{id: "{fid}"}}), (r:Requirement {{id: "{rid}"}})\n'
                f'MERGE (f)-[:INCLUDES_REQUIREMENT]->(r);'
            )
    cypher.append("")

    # =========================================================================
    # 10. SEMANTIC RELATIONSHIPS
    # =========================================================================
    cypher.append("// ===========================================================================")
    cypher.append("// --- 10. SEMANTIC RELATIONSHIPS ---")
    cypher.append("// ===========================================================================\n")

    # 10.1 Functional Dependencies (SEMANTICALLY_DEPENDS_ON)
    # Proximity unlock depends on digital key enrollment
    semantic_dependencies = [
        ("REQ-L3-002", "REQ-L3-001", "Proximity unlock semantically requires successful digital key provisioning and enrollment."),
        ("REQ-L3-003", "REQ-L3-002", "Ride authorization semantically requires vehicle to have been unlocked by valid proximity key."),
        ("REQ-L3-003", "REQ-L5-004", "Ride authorization requires authenticated identity token established during enrollment."),
        ("REQ-L3-004", "REQ-L3-001", "Shared key distribution requires an established primary key lifecycle infrastructure."),
        ("REQ-L3-005", "REQ-L3-004", "Key revocation acts upon active shared and enrolled keys."),
        ("REQ-L3-006", "REQ-L3-004", "Rider profile constraints are enforced on shared digital keys."),
        ("REQ-L3-007", "REQ-L3-004", "Valet temporary service key generation derives from shared key lifecycle mechanism."),
        ("REQ-L3-009", "REQ-L3-002", "Vehicle status display and telemetry depends on proximity connection link."),
        ("REQ-L3-010", "REQ-L3-003", "Offline grace mode is a contingency for ride authorization when cloud is unreachable.")
    ]
    cypher.append("// --- 10.1 Functional Precondition Dependencies (SEMANTICALLY_DEPENDS_ON) ---")
    for src, dst, rationale in semantic_dependencies:
        cypher.append(
            f'MATCH (a:Requirement {{id: "{src}"}}), (b:Requirement {{id: "{dst}"}})\n'
            f'MERGE (a)-[:SEMANTICALLY_DEPENDS_ON {{rationale: "{escape_str(rationale)}" }}]->(b);'
        )
    cypher.append("")

    # 10.2 Safety, Policy & Security Constraints (CONSTRAINS)
    semantic_constraints = [
        ("REQ-L3-005", "REQ-L3-010", "Revocation overrides offline grace: a revoked key must never be honored in offline mode."),
        ("REQ-L4-009", "REQ-L3-010", "72-hour hard limit strictly bounds the maximum allowable offline grace period."),
        ("REQ-L5-021", "REQ-L3-010", "Hard timeout logic immediately terminates offline operation upon window expiry."),
        ("REQ-L5-006", "REQ-L3-002", "Immediate crypto rejection constrains proximity unlock engine from false actuation."),
        ("REQ-L5-015", "REQ-L3-003", "Valet mode restricts ride authorization by capping vehicle speed to 20 km/h."),
        ("REQ-L5-016", "REQ-L3-003", "Valet mode restricts ride authorization by disabling trunk release and limiting speed.")
    ]
    cypher.append("// --- 10.2 Policy & Safety Constraints (CONSTRAINS) ---")
    for src, dst, rationale in semantic_constraints:
        cypher.append(
            f'MATCH (a:Requirement {{id: "{src}"}}), (b:Requirement {{id: "{dst}"}})\n'
            f'MERGE (a)-[:CONSTRAINS {{rationale: "{escape_str(rationale)}" }}]->(b);'
        )
    cypher.append("")

    # 10.3 Alternative Implementations (SEMANTICALLY_ALTERNATIVE_TO)
    # Different variants implement the same capability via different tech
    semantic_alternatives = [
        ("REQ-L5-003", "REQ-L5-004", "Base BLE RSSI threshold (-65 dBm) is an alternative proximity implementation to Premium UWB ranging."),
        ("REQ-L5-018", "REQ-L5-019", "Base REST polling (60s) is an alternative telemetry synchronization implementation to Premium WebSocket push."),
        ("REQ-L5-019", "REQ-L5-020", "Premium WebSocket push is an alternative to Fleet 10k batch WebSocket telemetry dashboard."),
        ("REQ-L5-001", "REQ-L5-002", "Base BLE discovery pairing is an alternative enrollment mechanism to Premium on-device biometric pairing."),
        ("REQ-L5-009", "REQ-L5-010", "Base time-based key expiry is an alternative sharing constraint mechanism to Premium geofencing."),
        ("REQ-L4-006", "REQ-L4-007", "Base 1-year log retention is an alternative compliance tier to Premium 5-year immutable WORM Data Lake.")
    ]
    cypher.append("// --- 10.3 Variant Divergence (SEMANTICALLY_ALTERNATIVE_TO) ---")
    for src, dst, rationale in semantic_alternatives:
        cypher.append(
            f'MATCH (a:Requirement {{id: "{src}"}}), (b:Requirement {{id: "{dst}"}})\n'
            f'MERGE (a)-[:SEMANTICALLY_ALTERNATIVE_TO {{rationale: "{escape_str(rationale)}" }}]->(b)\n'
            f'MERGE (b)-[:SEMANTICALLY_ALTERNATIVE_TO {{rationale: "{escape_str(rationale)}" }}]->(a);'
        )
    cypher.append("")

    # 10.4 Risk Mitigations (MITIGATES_RISK_OF)
    semantic_mitigations = [
        ("REQ-L5-004", "REQ-L5-003", "UWB precise ranging mitigates vulnerability to BLE signal relay and amplification attacks."),
        ("REQ-L5-037", "REQ-L3-038", "Centralized secrets manager mitigates hardcoded credentials and database credential leakage."),
        ("REQ-L4-037", "REQ-L3-037", "Automated container vulnerability scanning in CI/CD mitigates deployment of exploitable CVEs."),
        ("REQ-L4-038", "REQ-L3-001", "API Gateway 100 req/min rate limiting mitigates brute force enrollment and DDoS attacks."),
        ("REQ-L3-041", "REQ-L3-009", "Graceful offline action queueing in mobile app mitigates cloud communication failure lockout.")
    ]
    cypher.append("// --- 10.4 Risk & Vulnerability Mitigations (MITIGATES_RISK_OF) ---")
    for src, dst, rationale in semantic_mitigations:
        cypher.append(
            f'MATCH (a:Requirement {{id: "{src}"}}), (b:Requirement {{id: "{dst}"}})\n'
            f'MERGE (a)-[:MITIGATES_RISK_OF {{rationale: "{escape_str(rationale)}" }}]->(b);'
        )
    cypher.append("")

    # 10.5 Regulatory & Compliance Governance (GOVERNED_BY)
    semantic_compliance = [
        ("REQ-L5-038", "COMP-GDPR-ART17", "Right to be Forgotten API endpoint satisfies GDPR Article 17 erasure requirements."),
        ("REQ-L5-040", "COMP-GDPR-ART20", "Data Portability JSON export API satisfies GDPR Article 20 requirements."),
        ("REQ-L3-040", "COMP-CCPA-1798", "Opt-Out of Sale toggle satisfies California Consumer Privacy Act requirements."),
        ("REQ-L3-043", "COMP-WCAG-21AA", "Accessibility standards compliance governed by WCAG 2.1 Level AA."),
        ("REQ-L5-045", "COMP-ISO-8601", "API timestamp standard governed by ISO 8601 format."),
        ("REQ-L3-037", "COMP-TLS-13", "Network data encryption in transit governed by TLS 1.3 RFC 8446 standard."),
        ("REQ-L3-038", "COMP-NIST-AES256", "Database encryption at rest governed by NIST AES-256 standard.")
    ]
    cypher.append("// --- 10.5 Regulatory Governance (GOVERNED_BY) ---")
    for src, dst, rationale in semantic_compliance:
        cypher.append(
            f'MATCH (a:Requirement {{id: "{src}"}}), (c:ComplianceStandard {{id: "{dst}"}})\n'
            f'MERGE (a)-[:GOVERNED_BY {{rationale: "{escape_str(rationale)}" }}]->(c);'
        )
    cypher.append("")

    # 10.6 Ripple Impact Connections (RIPPLE_IMPACT_ON)
    # Demonstrating engineering ripple effects between requirements and components
    ripple_effects = [
        ("REQ-L3-002", "REQ-L4-002", "Changes to proximity zone threshold ripple directly to unlock latency calculation."),
        ("REQ-L4-002", "REQ-L5-003", "Latency requirements ripple into BLE RSSI moving average filter window and threshold."),
        ("REQ-L3-005", "REQ-L4-005", "Revocation requirement changes ripple into online propagation latency bound."),
        ("REQ-L3-010", "REQ-L4-009", "Offline grace policies ripple into vehicle controller memory retention limits.")
    ]
    cypher.append("// --- 10.6 Ripple Impact Propagation (RIPPLE_IMPACT_ON) ---")
    for src, dst, rationale in ripple_effects:
        cypher.append(
            f'MATCH (a:Requirement {{id: "{src}"}}), (b:Requirement {{id: "{dst}"}})\n'
            f'MERGE (a)-[:RIPPLE_IMPACT_ON {{rationale: "{escape_str(rationale)}" }}]->(b);'
        )
    cypher.append("")

    # Verification query
    cypher.append("// --- 11. Verification Query ---")
    cypher.append("MATCH (n) RETURN labels(n) as EntityType, count(*) as Count ORDER BY Count DESC;")
    cypher.append("MATCH ()-[r]->() RETURN type(r) as RelationshipType, count(*) as Count ORDER BY Count DESC;")

    # Write Cypher File
    cypher_content = "\n".join(cypher)
    with open(OUTPUT_CYPHER, "w", encoding="utf-8") as f:
        f.write(cypher_content)

    print(f"Generated Cypher script: {OUTPUT_CYPHER}")

    # Now write the JSON Graph Seed for offline in-memory execution in neo4j_tools.py
    seed_nodes = {}
    seed_edges = []

    # Requirements
    for req in req_rows:
        rid = req["Requirement ID"].strip()
        seed_nodes[rid] = {
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
            "oems": [x.strip() for x in req.get("OEM Customization Flag", "").split(",") if x.strip()],
            "notes": req.get("Variant Implementation Notes", "").strip()
        }

        parent = req.get("Parent Requirement", "").strip()
        if parent and parent.lower() != "none":
            seed_edges.append({"from": rid, "rel": "CHILD_OF", "to": parent, "category": "direct"})
            seed_edges.append({"from": parent, "rel": "PARENT_OF", "to": rid, "category": "direct"})

        comp = req.get("Business Component", "").strip()
        if comp:
            cid = f"COMP-{comp.replace(' ', '_').upper()}"
            if cid not in seed_nodes:
                seed_nodes[cid] = {"id": cid, "type": "Component", "name": comp}
            seed_edges.append({"from": rid, "rel": "ALLOCATED_TO", "to": cid, "category": "direct"})

        for v in [x.strip() for x in req.get("Target Variant", "").split(",") if x.strip()]:
            if v not in seed_nodes:
                seed_nodes[v] = {"id": v, "type": "Variant", "name": v}
            seed_edges.append({"from": rid, "rel": "TARGETS_VARIANT", "to": v, "category": "direct"})

        for o in [x.strip() for x in req.get("OEM Customization Flag", "").split(",") if x.strip()]:
            if o not in seed_nodes:
                seed_nodes[o] = {"id": o, "type": "OEM", "name": o}
            seed_edges.append({"from": rid, "rel": "APPLICABLE_TO_OEM", "to": o, "category": "direct"})

        for tc in [x.strip() for x in req.get("Test Cases Linked", "").split(",") if x.strip()]:
            if tc not in seed_nodes:
                seed_nodes[tc] = {"id": tc, "type": "TestCase", "name": tc}
            seed_edges.append({"from": rid, "rel": "VERIFIED_BY", "to": tc, "category": "direct"})
            seed_edges.append({"from": tc, "rel": "VERIFIES", "to": rid, "category": "direct"})

    # Compliance
    for cp in compliance_standards:
        seed_nodes[cp["id"]] = {"id": cp["id"], "type": "ComplianceStandard", "name": cp["name"], "description": cp["description"]}

    # Features
    for f_item in features:
        seed_nodes[f_item["id"]] = {"id": f_item["id"], "type": "Feature", "name": f_item["name"], "description": f_item["desc"]}

    # Feature edges
    for fid, req_list in feature_mappings:
        for rid in req_list:
            seed_edges.append({"from": fid, "rel": "INCLUDES_REQUIREMENT", "to": rid, "category": "direct"})

    # Semantic edges
    for src, dst, rationale in semantic_dependencies:
        seed_edges.append({"from": src, "rel": "SEMANTICALLY_DEPENDS_ON", "to": dst, "rationale": rationale, "category": "semantic"})

    for src, dst, rationale in semantic_constraints:
        seed_edges.append({"from": src, "rel": "CONSTRAINS", "to": dst, "rationale": rationale, "category": "semantic"})

    for src, dst, rationale in semantic_alternatives:
        seed_edges.append({"from": src, "rel": "SEMANTICALLY_ALTERNATIVE_TO", "to": dst, "rationale": rationale, "category": "semantic"})
        seed_edges.append({"from": dst, "rel": "SEMANTICALLY_ALTERNATIVE_TO", "to": src, "rationale": rationale, "category": "semantic"})

    for src, dst, rationale in semantic_mitigations:
        seed_edges.append({"from": src, "rel": "MITIGATES_RISK_OF", "to": dst, "rationale": rationale, "category": "semantic"})

    for src, dst, rationale in semantic_compliance:
        seed_edges.append({"from": src, "rel": "GOVERNED_BY", "to": dst, "rationale": rationale, "category": "semantic"})

    for src, dst, rationale in ripple_effects:
        seed_edges.append({"from": src, "rel": "RIPPLE_IMPACT_ON", "to": dst, "rationale": rationale, "category": "semantic"})

    # Test cases details from tc_rows
    for tc in tc_rows:
        tcid = tc.get("Test Case ID", "").strip()
        if tcid in seed_nodes:
            seed_nodes[tcid].update({
                "description": tc.get("Test Description", ""),
                "type": tc.get("Test Type", ""),
                "priority": tc.get("Priority", ""),
                "status": tc.get("Status", ""),
                "owner": tc.get("Owner", ""),
                "suite_id": tc.get("Test Suite ID", "")
            })

    seed_data = {
        "metadata": {
            "title": "AXIOM E-Key 2W Digital Key Platform Knowledge Graph",
            "total_nodes": len(seed_nodes),
            "total_edges": len(seed_edges),
            "direct_relationships_count": sum(1 for e in seed_edges if e.get("category") == "direct"),
            "semantic_relationships_count": sum(1 for e in seed_edges if e.get("category") == "semantic")
        },
        "nodes": seed_nodes,
        "edges": seed_edges
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2)

    print(f"Generated JSON seed: {OUTPUT_JSON} with {len(seed_nodes)} nodes and {len(seed_edges)} edges!")
    print(f"- Direct edges: {seed_data['metadata']['direct_relationships_count']}")
    print(f"- Semantic edges: {seed_data['metadata']['semantic_relationships_count']}")


if __name__ == "__main__":
    build_graph()
