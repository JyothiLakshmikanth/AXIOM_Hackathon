"""
AXIOM Data Loader — BigQuery + Vertex AI Embeddings
====================================================
Loads 4 CSVs into BigQuery (axiom_data dataset) and generates
text embeddings using BigQuery ML for semantic search.

Usage:
    python data/load_to_bigquery.py --project axiom-510516

Requirements (already in requirements.txt):
    google-cloud-bigquery
    google-cloud-aiplatform
    pandas
"""

import argparse
import os
import logging
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("axiom.loader")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATASET_ID = "axiom_data"
LOCATION = "US"  # BigQuery dataset location

DATA_DIR = Path(__file__).parent  # same directory as this script


def _sprint_text(row) -> str:
    return (
        f"Type: {row['Type']}. "
        f"ID: {row['Id']}. "
        f"Summary: {row['Summary']}. "
        f"Status: {row['Status']}. "
        f"Priority: {row['Priority']}. "
        f"Team: {row['Team']}. "
        f"Sprint: {row['Sprint']}. "
        f"Components: {row['Components']}. "
        f"Filed Against: {row['Filed_Against']}. "
        f"Labels: {row.get('labels', '')}."
    )


def _pi_text(row) -> str:
    return (
        f"PI: {row['PI_Name']} ({row['PI_ID']}). "
        f"Focus: {row['Focus_Area']}. "
        f"Milestones: {row['Key_Milestones']}. "
        f"Status: {row['Status']}. "
        f"Risk: {row['Risk_Level']}. "
        f"Notes: {row['Notes']}."
    )


def _capacity_text(row) -> str:
    res_id = row.get("Default_Assignee_ID", row.get("Resource_ID", ""))
    return (
        f"Associate: {row['Associate']} ({res_id}). "
        f"Role: {row['Role']}. "
        f"Domain: {row['Domain']}. "
        f"Location: {row['Location']}. "
        f"Allocation: {row['Allocation_%']}%. "
        f"Status: {row['Availability_Status']}. "
        f"Notes: {row.get('Notes', '')}."
    )


def _competency_text(row) -> str:
    gap = ""
    try:
        exp = int(str(row["expected_level"]).replace("L", ""))
        cur = int(str(row["current_level"]).replace("L", ""))
        gap = "gap" if cur < exp else ("exceeds" if cur > exp else "meets")
    except Exception:
        gap = "unknown"
    return (
        f"Associate: {row['associate']}. "
        f"Role: {row['role']}. "
        f"Domain: {row['domain']}. "
        f"Skill: {row['skill']}. "
        f"Expected level: {row['expected_level']}, Current level: {row['current_level']}. "
        f"Competency status: {gap} expectation. "
        f"Experience: {row['experience']} years."
    )


def _test_case_text(row) -> str:
    return (
        f"Test Case: {row.get('Test Case ID', '')}. "
        f"Objective: {row.get('Test Objective', '')}. "
        f"Description: {row.get('Test Description', '')}. "
        f"Type: {row.get('Test Type', '')}. "
        f"Priority: {row.get('Priority', '')}. "
        f"Status: {row.get('Status', '')}. "
        f"Variant: {row.get('Target Variant', '')}."
    )


# Only Resource, Test, Sprint, and PI data go into BigQuery.
# Requirements data (requirements_master_v5.csv) is intentionally excluded
# because it is managed in Neo4j.
TABLE_CONFIG = {
    # Project & Sprint / PI Planning
    "sprint_planning": ("AXIOM_Sprint_Planning.csv", _sprint_text),
    "pi_planning": ("AXIOM_PI_Planning_2026.csv", _pi_text),
    # Resource & Competency Planning
    "capacity_planning": ("AXIOM_Capacity_Planning.csv", _capacity_text),
    "competency_matrix": ("AXIOM_Competency_Matrix.csv", _competency_text),
    # Test Data (tabular)
    "test_cases": ("test_cases_master_v5.csv", _test_case_text),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_client(project: str) -> bigquery.Client:
    return bigquery.Client(project=project)


def ensure_dataset(client: bigquery.Client, project: str) -> None:
    dataset_ref = f"{project}.{DATASET_ID}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = LOCATION
    dataset.description = "AXIOM project planning and team data"
    client.create_dataset(dataset, exists_ok=True)
    log.info("Dataset %s ready.", dataset_ref)


def load_csv_to_bq(
    client: bigquery.Client,
    project: str,
    table_name: str,
    csv_file: str,
    text_fn,
) -> None:
    csv_path = DATA_DIR / csv_file
    if not csv_path.exists():
        log.warning("CSV not found: %s — skipping", csv_path)
        return

    log.info("Loading %s -> %s.%s.%s", csv_file, project, DATASET_ID, table_name)

    df = pd.read_csv(csv_path)
    df = df.dropna(how="all")  # drop empty trailing rows

    # Add embedding text column
    df["text_for_embedding"] = df.apply(text_fn, axis=1)

    # Sanitize column names for BigQuery (replace % and invalid chars with _)
    df.columns = [c.replace("%", "pct").replace(" ", "_") for c in df.columns]
    import re
    df.columns = [re.sub(r"[^a-zA-Z0-9_]", "_", c) for c in df.columns]

    table_ref = f"{project}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # overwrite on re-run
        autodetect=True,
    )

    try:
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    except Exception as exc:
        if "pyarrow" in str(exc).lower():
            log.info("  pyarrow not installed, using load_table_from_json fallback...")
            records = df.where(pd.notnull(df), None).to_dict(orient="records")
            job = client.load_table_from_json(records, table_ref, job_config=job_config)
        else:
            raise exc
    job.result()  # wait

    table = client.get_table(table_ref)
    log.info(
        "  Loaded %d rows, %d columns -> %s",
        table.num_rows,
        len(table.schema),
        table_ref,
    )


def load_test_cases_embeddings_ndjson(client: bigquery.Client, project: str) -> None:
    """
    Loads test_cases_with_embeddings.ndjson into BigQuery table `test_cases_embeddings`.
    This table contains pre-computed 768-dimension Gemini vector embeddings.
    """
    ndjson_path = DATA_DIR / "test_cases_with_embeddings.ndjson"
    if not ndjson_path.exists():
        log.warning("NDJSON not found: %s — skipping", ndjson_path)
        return

    table_name = "test_cases_embeddings"
    table_ref = f"{project}.{DATASET_ID}.{table_name}"
    log.info("Loading pre-embedded test cases: %s -> %s", ndjson_path.name, table_ref)

    schema = [
        bigquery.SchemaField("test_plan_id", "STRING"),
        bigquery.SchemaField("test_suite_id", "STRING"),
        bigquery.SchemaField("test_case_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("test_description", "STRING"),
        bigquery.SchemaField("linked_req_ids", "STRING", mode="REPEATED"),
        bigquery.SchemaField("test_type", "STRING"),
        bigquery.SchemaField("test_objective", "STRING"),
        bigquery.SchemaField("pre_conditions", "STRING"),
        bigquery.SchemaField("test_steps", "STRING"),
        bigquery.SchemaField("expected_result", "STRING"),
        bigquery.SchemaField("priority", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("owner", "STRING"),
        bigquery.SchemaField("target_variant", "STRING", mode="REPEATED"),
        bigquery.SchemaField("embedded_text", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
    ]

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with open(ndjson_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
    job.result()

    table = client.get_table(table_ref)
    log.info(
        "  Loaded %d test cases with 768-dim vector embeddings -> %s",
        table.num_rows,
        table_ref,
    )

    # Optionally create vector index for fast semantic cosine similarity search
    try:
        index_sql = f"""
        CREATE VECTOR INDEX IF NOT EXISTS test_cases_vector_idx
        ON `{project}.{DATASET_ID}.{table_name}`(embedding)
        OPTIONS(
            index_type = 'IVF',
            distance_type = 'COSINE'
        );
        """
        client.query(index_sql).result()
        log.info("  Vector index 'test_cases_vector_idx' created/ready.")
    except Exception as exc:
        log.info("  Note on vector index: %s (requires adequate table data/pricing tier)", exc)


def setup_bqml_embedding_model(client: bigquery.Client, project: str) -> None:
    """
    Create a BigQuery ML remote model backed by Vertex AI text-embedding-004.
    Requires a pre-configured BQ -> Vertex AI remote connection named 'vertex-ai-conn'.

    Setup steps (run once in Cloud Shell):
      bq mk --connection --location=US --project_id=PROJECT \\
             --connection_type=CLOUD_RESOURCE vertex-ai-conn
      # Then grant the generated SA the aiplatform.user role.
    """
    connection = f"`{project}.us.vertex-ai-conn`"
    model_ref = f"`{project}.{DATASET_ID}.axiom_embedding_model`"
    endpoint = (
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}"
        f"/locations/us-central1/publishers/google/models/text-embedding-004"
    )

    ddl = f"""
    CREATE OR REPLACE MODEL {model_ref}
    REMOTE WITH CONNECTION {connection}
    OPTIONS (endpoint = '{endpoint}')
    """

    log.info("Creating BQML embedding model ...")
    query_job = client.query(ddl)
    query_job.result()
    log.info("  Embedding model ready: %s", model_ref)


def generate_and_store_embeddings(client: bigquery.Client, project: str) -> None:
    """
    For each table, generate embeddings on text_for_embedding and store them
    in a separate _embeddings table that can be used with VECTOR_SEARCH.
    """
    for table_name in TABLE_CONFIG:
        src = f"`{project}.{DATASET_ID}.{table_name}`"
        dst = f"`{project}.{DATASET_ID}.{table_name}_embeddings`"
        model = f"`{project}.{DATASET_ID}.axiom_embedding_model`"

        sql = f"""
        CREATE OR REPLACE TABLE {dst} AS
        SELECT *
        FROM ML.GENERATE_EMBEDDING(
          MODEL {model},
          (SELECT *, text_for_embedding AS content FROM {src}),
          STRUCT(TRUE AS flatten_json_output)
        )
        """

        log.info("Generating embeddings for %s ...", table_name)
        client.query(sql).result()
        log.info("  Embeddings stored in %s", dst)


def print_sample_queries(project: str) -> None:
    p = project
    d = DATASET_ID
    print("\n" + "=" * 70)
    print("SAMPLE QUERIES FOR BIGQUERY CONSOLE")
    print("=" * 70)
    print(f"""
-- 1. All open critical bugs
SELECT Id, Summary, Team, Sprint, Status
FROM `{p}.{d}.sprint_planning`
WHERE Type = 'Bug' AND Priority = 'Critical' AND Status = 'Open';

-- 2. Sprint velocity (story points done per sprint)
SELECT Sprint, SUM(Story_Points) AS total_points, COUNT(*) AS items
FROM `{p}.{d}.sprint_planning`
WHERE Status = 'Done'
GROUP BY Sprint ORDER BY Sprint;

-- 3. Team capacity Q1 2026
SELECT Associate, Role, Domain, Q1_2026_Hours, Allocation_pct
FROM `{p}.{d}.capacity_planning`
ORDER BY Q1_2026_Hours DESC;

-- 4. Competency gaps (current_level < expected_level)
SELECT associate, role, skill, expected_level, current_level
FROM `{p}.{d}.competency_matrix`
WHERE current_level < expected_level;

-- 5. Test cases vector search (matches defects/descriptions to test cases)
SELECT base.test_case_id, base.test_objective, base.test_type, base.priority, distance
FROM VECTOR_SEARCH(
  TABLE `{p}.{d}.test_cases_embeddings`,
  'embedding',
  (SELECT embedding FROM `{p}.{d}.test_cases_embeddings` WHERE test_case_id = 'TC-ENR-001'),
  top_k => 5,
  distance_type => 'COSINE'
);
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Load AXIOM CSVs to BigQuery")
    parser.add_argument(
        "--project",
        default=os.getenv("GOOGLE_CLOUD_PROJECT", "axiom-510516"),
        help="GCP project ID",
    )
    parser.add_argument(
        "--with-embeddings",
        action="store_true",
        default=False,
        help=(
            "Also create BQML embedding model and generate vector embeddings. "
            "Requires Vertex AI remote connection 'vertex-ai-conn' to be set up first."
        ),
    )
    args = parser.parse_args()

    project = args.project
    log.info("Project: %s | Dataset: %s", project, DATASET_ID)

    client = get_client(project)

    # Step 1: ensure dataset
    ensure_dataset(client, project)

    # Step 2: load CSVs (Sprint, PI, Capacity, Competency, Test Cases)
    for table_name, (csv_file, text_fn) in TABLE_CONFIG.items():
        load_csv_to_bq(client, project, table_name, csv_file, text_fn)

    # Step 3: load pre-embedded test cases (with 768-dim vector embeddings)
    load_test_cases_embeddings_ndjson(client, project)

    # Step 4 (optional): generate additional embeddings if requested
    if args.with_embeddings:
        setup_bqml_embedding_model(client, project)
        generate_and_store_embeddings(client, project)
    else:
        log.info(
            "Skipped extra BQML embedding model generation. "
            "Pre-embedded test cases are already loaded into 'test_cases_embeddings'!"
        )

    print_sample_queries(project)
    log.info("All resource, project, sprint, PI, and test tables loaded into '%s'.", DATASET_ID)


if __name__ == "__main__":
    main()
