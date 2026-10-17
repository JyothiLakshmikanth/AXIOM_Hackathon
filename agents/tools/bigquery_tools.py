"""
BigQuery Analytics & Structured Project Facts Tools for AXIOM.
Queries real BigQuery tables in the `axiom_data` dataset:
  - axiom_data.sprint_planning       (AXIOM_Sprint_Planning.csv)
  - axiom_data.capacity_planning     (AXIOM_Capacity_Planning.csv)
  - axiom_data.competency_matrix     (AXIOM_Competency_Matrix.csv)
  - axiom_data.pi_planning           (AXIOM_PI_Planning_2026.csv)
  - axiom_data.test_cases            (test_cases_master_v5.csv)

Falls back to local CSVs in data/ when GCP credentials are not present.
"""

import os
import csv
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("axiom.tools.bigquery")

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "axiom-cloud-run")
_DATASET = "axiom_data"
_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data"
)

# Mapping: BQ table name → local CSV filename
_TABLE_CSV_MAP = {
    "sprint_planning": "AXIOM_Sprint_Planning.csv",
    "capacity_planning": "AXIOM_Capacity_Planning.csv",
    "competency_matrix": "AXIOM_Competency_Matrix.csv",
    "pi_planning": "AXIOM_PI_Planning_2026.csv",
    "test_cases": "test_cases_master_v5.csv",
}

# ──────────────────────────────────────────────────────────────────────────────
# BQ client (lazy singleton)
# ──────────────────────────────────────────────────────────────────────────────
_bq_client = None
_bq_attempted = False


def _get_bq_client():
    global _bq_client, _bq_attempted
    if _bq_attempted:
        return _bq_client
    _bq_attempted = True
    # Fast path: if no credentials file or project specified, don't block on network metadata timeouts
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and not os.getenv("GCP_PROJECT"):
        logger.info("No GCP credentials in environment. Using local CSV data directly.")
        _bq_client = None
        return None
    try:
        from google.cloud import bigquery  # noqa: F401
        _bq_client = bigquery.Client(project=_PROJECT_ID)
        logger.info("BigQuery client initialised (project=%s)", _PROJECT_ID)
        return _bq_client
    except Exception as e:
        logger.warning("BigQuery client unavailable (%s). Using local CSV fallback.", e)
        _bq_client = None
        return None


def _run_bq_query(sql: str) -> List[Dict[str, Any]]:
    """Execute a BigQuery SQL query and return rows as list-of-dicts."""
    client = _get_bq_client()
    if client is None:
        return []
    try:
        rows = client.query(sql).result()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.warning("BigQuery query failed (%s). Falling back to CSV.", e)
        return []


def _load_csv(table_name: str) -> List[Dict[str, Any]]:
    """Load a local CSV file for the given table name."""
    filename = _TABLE_CSV_MAP.get(table_name)
    if not filename:
        logger.error("No CSV mapping for table: %s", table_name)
        return []
    path = os.path.join(_DATA_DIR, filename)
    if not os.path.exists(path):
        logger.error("CSV not found: %s", path)
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ──────────────────────────────────────────────────────────────────────────────
# DEFECT / SPRINT functions  (defect_agent uses these)
# ──────────────────────────────────────────────────────────────────────────────

def bigquery_list_open_defects_by_sprint(sprint_id: str) -> List[Dict[str, Any]]:
    """
    Lists open bug/defect work items for a sprint from axiom_data.sprint_planning.
    Columns: Type, Id, Summary, Sprint_ID, Status, Priority, Story_Points, Assignee...
    """
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.sprint_planning`
        WHERE Sprint_ID = '{sprint_id}'
          AND Type = 'Bug'
          AND Status = 'Open'
        ORDER BY Priority ASC
        LIMIT 50
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows
    all_rows = _load_csv("sprint_planning")
    return [
        r for r in all_rows
        if r.get("Sprint_ID") == sprint_id
        and r.get("Type") == "Bug"
        and r.get("Status") == "Open"
    ]


def bigquery_list_all_defects() -> List[Dict[str, Any]]:
    """
    Returns all defect/bug records from axiom_data.sprint_planning.
    Falls back to local AXIOM_Sprint_Planning.csv.
    """
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.sprint_planning`
        WHERE Type = 'Bug'
        ORDER BY Priority ASC
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows
    all_rows = _load_csv("sprint_planning")
    return [r for r in all_rows if r.get("Type") == "Bug"]


def bigquery_get_defect_by_issue_id(issue_id: str) -> Dict[str, Any]:
    """
    Retrieves a defect record from axiom_data.sprint_planning by issue Id.
    Handles aliases such as GH-ISSUE-107 <-> TWK-107 or numeric matching.
    Falls back to local CSV if BQ is unavailable.
    """
    if not issue_id:
        return {"error": "No issue_id provided"}

    # Resolve aliases (e.g., GH-ISSUE-107 -> TWK-107)
    candidate_ids = [issue_id]
    if "GH-ISSUE-" in issue_id.upper():
        candidate_ids.append(issue_id.upper().replace("GH-ISSUE-", "TWK-"))
    elif "TWK-" in issue_id.upper():
        candidate_ids.append(issue_id.upper().replace("TWK-", "GH-ISSUE-"))
    
    # Try digits extraction
    import re
    digits = re.findall(r"\d+", issue_id)
    if digits:
        candidate_ids.append(f"TWK-{digits[0]}")
        candidate_ids.append(f"GH-ISSUE-{digits[0]}")

    id_conditions = " OR ".join([f"Id = '{cid}'" for cid in candidate_ids])
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.sprint_planning`
        WHERE ({id_conditions})
          AND Type = 'Bug'
        LIMIT 1
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows[0]

    all_rows = _load_csv("sprint_planning")
    for r in all_rows:
        row_id = r.get("Id", "")
        if r.get("Type") == "Bug" and (row_id in candidate_ids or any(cid in row_id for cid in candidate_ids)):
            return r
    return {"error": f"Defect {issue_id} not found."}


def bigquery_get_team_velocity_history(sprint_id: str) -> Dict[str, Any]:
    """
    Computes rolling velocity and volatility by aggregating Story_Points
    from axiom_data.sprint_planning across all sprints.
    """
    sql = f"""
        SELECT
            Sprint_ID,
            SUM(SAFE_CAST(Story_Points AS FLOAT64)) AS total_points,
            SUM(CASE WHEN Status IN ('Done','Closed')
                     THEN SAFE_CAST(Story_Points AS FLOAT64) ELSE 0 END) AS completed_points,
            COUNT(*) AS total_tasks
        FROM `{_PROJECT_ID}.{_DATASET}.sprint_planning`
        GROUP BY Sprint_ID
        ORDER BY Sprint_ID
    """
    rows = _run_bq_query(sql)
    if not rows:
        # CSV fallback: aggregate locally
        all_rows = _load_csv("sprint_planning")
        agg: Dict[str, Dict] = {}
        for r in all_rows:
            sid = r.get("Sprint_ID", "")
            if not sid:
                continue
            if sid not in agg:
                agg[sid] = {"Sprint_ID": sid, "total_points": 0.0, "completed_points": 0.0, "total_tasks": 0}
            try:
                pts = float(r.get("Story_Points") or 0)
            except (ValueError, TypeError):
                pts = 0.0
            agg[sid]["total_points"] += pts
            agg[sid]["total_tasks"] += 1
            if r.get("Status") in ("Done", "Closed"):
                agg[sid]["completed_points"] += pts
        rows = list(agg.values())

    completed_vals = [float(r.get("completed_points") or 0) for r in rows]
    rolling_avg = sum(completed_vals) / max(1, len(completed_vals))
    variance = sum((x - rolling_avg) ** 2 for x in completed_vals) / max(1, len(completed_vals))
    std_dev = variance ** 0.5
    volatility = std_dev / max(1.0, rolling_avg)

    current = next((r for r in rows if r.get("Sprint_ID") == sprint_id), rows[-1] if rows else {})
    committed = float(current.get("total_points") or 0)
    completed = float(current.get("completed_points") or 0)

    return {
        "sprint_id": sprint_id,
        "rolling_average_velocity": round(rolling_avg, 2),
        "volatility_index": round(volatility, 3),
        "current_sprint_committed": committed,
        "current_sprint_completed": completed,
        "slip_risk": "HIGH" if completed + (rolling_avg * 0.3) < committed else "LOW",
        "history": [
            {"sprint_id": r["Sprint_ID"], "completed": r.get("completed_points")} for r in rows
        ],
    }


def bigquery_get_sprint_tasks(sprint_id: str) -> List[Dict[str, Any]]:
    """Returns all tasks for a sprint from axiom_data.sprint_planning."""
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.sprint_planning`
        WHERE Sprint_ID = '{sprint_id}'
        ORDER BY Priority ASC
        LIMIT 200
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows
    all_rows = _load_csv("sprint_planning")
    return [r for r in all_rows if r.get("Sprint_ID") == sprint_id]


# ──────────────────────────────────────────────────────────────────────────────
# CAPACITY & COMPETENCY  (resource_agent uses these)
# ──────────────────────────────────────────────────────────────────────────────

def bigquery_get_team_capacity(resource_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves team capacity records from axiom_data.capacity_planning.
    Columns: Associate, Default_Assignee_ID, Role, Domain, Allocation_%, Location,
             Q1_2026_Hours, Q2_2026_Hours, Q3_2026_Hours, Q4_2026_Hours,
             Availability_Status, Notes
    """
    where = f"WHERE Default_Assignee_ID = '{resource_id}'" if resource_id else ""
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.capacity_planning`
        {where}
        LIMIT 100
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows
    all_rows = _load_csv("capacity_planning")
    if resource_id:
        return [r for r in all_rows if r.get("Default_Assignee_ID") == resource_id]
    return all_rows


def bigquery_get_competency_matrix(associate: Optional[str] = None,
                                   skill: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves competency records from axiom_data.competency_matrix.
    Columns: source, associate, experience, role, feature, domain, skill,
             expected_level, current_level
    """
    conditions = []
    if associate:
        conditions.append(f"LOWER(associate) LIKE '%{associate.lower()}%'")
    if skill:
        conditions.append(f"LOWER(skill) LIKE '%{skill.lower()}%'")
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.competency_matrix`
        {where}
        ORDER BY associate, skill
        LIMIT 200
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows
    all_rows = _load_csv("competency_matrix")
    if associate:
        all_rows = [r for r in all_rows if associate.lower() in r.get("associate", "").lower()]
    if skill:
        all_rows = [r for r in all_rows if skill.lower() in r.get("skill", "").lower()]
    return all_rows


def bigquery_get_pi_planning(pi_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves PI planning records from axiom_data.pi_planning.
    Columns: PI_ID, PI_Name, Start_Date, End_Date, Duration_Weeks, Focus_Area,
             Key_Milestones, Status, Target_Completion, Quality_Gate, Risk_Level, Notes
    """
    where = f"WHERE PI_ID = '{pi_id}'" if pi_id else ""
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.pi_planning`
        {where}
        ORDER BY Start_Date
        LIMIT 50
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows
    all_rows = _load_csv("pi_planning")
    if pi_id:
        return [r for r in all_rows if r.get("PI_ID") == pi_id]
    return all_rows


# ──────────────────────────────────────────────────────────────────────────────
# TEST CASES  (test_agent uses these)
# ──────────────────────────────────────────────────────────────────────────────

def bigquery_get_test_run_results(test_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves test case records from axiom_data.test_cases.
    Columns: Test Plan ID, Test Suite ID, Test Case ID, Test Description,
             Linked Req IDs, Test Type, Test Objective, Pre-conditions,
             Test Steps (Summary), Expected Result, Priority, Status, Owner, Target Variant
    """
    where = f"WHERE `Test Case ID` = '{test_id}'" if test_id else ""
    sql = f"""
        SELECT *
        FROM `{_PROJECT_ID}.{_DATASET}.test_cases`
        {where}
        ORDER BY Priority ASC
        LIMIT 100
    """
    rows = _run_bq_query(sql)
    if rows:
        return rows
    all_rows = _load_csv("test_cases")
    if test_id:
        return [r for r in all_rows if r.get("Test Case ID") == test_id]
    return all_rows


def bigquery_get_coverage_summary(module_name: str) -> Dict[str, Any]:
    """
    Returns test coverage summary for a module from axiom_data.test_cases.
    Searches Test Description and Test Objective columns.
    """
    sql = f"""
        SELECT
            `Test Type`,
            COUNT(*) AS total,
            COUNTIF(Status = 'Active') AS active,
            COUNTIF(Priority = 'High') AS high_priority
        FROM `{_PROJECT_ID}.{_DATASET}.test_cases`
        WHERE LOWER(`Test Description`) LIKE '%{module_name.lower()}%'
           OR LOWER(`Test Objective`)   LIKE '%{module_name.lower()}%'
        GROUP BY `Test Type`
    """
    rows = _run_bq_query(sql)
    if not rows:
        all_rows = _load_csv("test_cases")
        filtered = [
            r for r in all_rows
            if module_name.lower() in r.get("Test Description", "").lower()
            or module_name.lower() in r.get("Test Objective", "").lower()
        ]
        total = len(filtered)
        active = sum(1 for r in filtered if r.get("Status") == "Active")
        high = sum(1 for r in filtered if r.get("Priority") == "High")
        rows = [{"Test Type": "All", "total": total, "active": active, "high_priority": high}]

    total = sum(int(r.get("total") or 0) for r in rows)
    active = sum(int(r.get("active") or 0) for r in rows)
    return {
        "module": module_name,
        "total_test_cases": total,
        "active_test_cases": active,
        "coverage_breakdown": rows,
        "risk_assessment": (
            "CRITICAL_GAP" if total == 0 else
            "LOW_COVERAGE" if active < total * 0.5 else
            "ACCEPTABLE"
        ),
    }


def bigquery_get_test_cases_embeddings(test_case_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves test case specs with 768-dim embeddings from local JSON cache
    (data/test_cases_with_embeddings.json) pre-computed by text-embedding-004.
    """
    json_path = os.path.join(_DATA_DIR, "test_cases_with_embeddings.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if test_case_id:
                return [d for d in data if d.get("test_case_id") == test_case_id]
            return data
        except Exception as e:
            logger.error("Error reading embedded test cases: %s", e)
    return []


def bigquery_vector_search_test_cases(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic similarity search on test cases.
    1. Tries BigQuery VECTOR_SEARCH on axiom_data.test_cases_embeddings (text-embedding-004).
    2. Falls back to local cosine similarity on pre-computed embeddings JSON.
    """
    import math
    import hashlib

    # ── Try live BigQuery VECTOR_SEARCH ──────────────────────────────────────
    client = _get_bq_client()
    if client:
        try:
            from vertexai.language_models import TextEmbeddingModel
            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embedding = model.get_embeddings([query_text])[0].values
            embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"
            sql = f"""
                SELECT base.test_case_id, base.description, base.test_type, base.priority,
                       distance AS cosine_distance
                FROM VECTOR_SEARCH(
                    TABLE `{_PROJECT_ID}.{_DATASET}.test_cases_embeddings`,
                    'embedding',
                    (SELECT {embedding_str} AS embedding),
                    top_k => {top_k},
                    distance_type => 'COSINE'
                )
                ORDER BY distance ASC
            """
            rows = client.query(sql).result()
            results = [dict(row) for row in rows]
            if results:
                logger.info("BigQuery VECTOR_SEARCH returned %d results.", len(results))
                return results
        except Exception as e:
            logger.warning("BigQuery VECTOR_SEARCH failed (%s). Using local fallback.", e)

    # ── Local cosine similarity fallback ─────────────────────────────────────
    records = bigquery_get_test_cases_embeddings()
    if not records:
        return []

    dim = 768
    q_vec = [0.0] * dim
    words = query_text.lower().split()
    for idx, word in enumerate(words):
        h = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
        slot = h % dim
        q_vec[slot] += math.sin(idx + 1) * math.cos(h % 1000)

    q_norm = math.sqrt(sum(x * x for x in q_vec))
    if q_norm > 0:
        q_vec = [x / q_norm for x in q_vec]

    scored = []
    for r in records:
        emb = r.get("embedding", [])
        if not emb or len(emb) != dim:
            continue
        dot = sum(q * e for q, e in zip(q_vec, emb))
        scored.append((dot, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for sim, r in scored[:top_k]:
        item = dict(r)
        item["cosine_similarity"] = round(sim, 4)
        item.pop("embedding", None)  # strip raw embedding from output
        results.append(item)
    return results
