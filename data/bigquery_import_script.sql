-- =============================================================================
-- AXIOM: BigQuery Test Cases with text-embedding-004 Vector Embeddings
-- Table: `axiom-cloud-run.axiom_qa.test_cases_embeddings`
-- Vector Dimension: 768
-- =============================================================================

-- 1. Create Dataset if it does not exist
CREATE SCHEMA IF NOT EXISTS `axiom-cloud-run.axiom_qa`
OPTIONS(location='us-central1');

-- 2. Create Table with Vector Embedding Column
CREATE TABLE IF NOT EXISTS `axiom-cloud-run.axiom_qa.test_cases_embeddings` (
    test_plan_id STRING,
    test_suite_id STRING,
    test_case_id STRING NOT NULL,
    test_description STRING,
    linked_req_ids ARRAY<STRING>,
    test_type STRING,
    test_objective STRING,
    pre_conditions STRING,
    test_steps STRING,
    expected_result STRING,
    priority STRING,
    status STRING,
    owner STRING,
    target_variant ARRAY<STRING>,
    embedded_text STRING,
    embedding ARRAY<FLOAT64>,
    created_at TIMESTAMP
);

-- 3. Create BigQuery Vector Search Index (Cosine Distance)
CREATE VECTOR INDEX IF NOT EXISTS test_cases_vector_idx
ON `axiom-cloud-run.axiom_qa.test_cases_embeddings`(embedding)
OPTIONS(
    index_type = 'IVF',
    distance_type = 'COSINE'
);

-- 4. Example: BigQuery Vector Search Query
-- Searches for test cases matching a free-text defect query:
/*
SELECT 
    base.test_case_id,
    base.test_objective,
    base.test_description,
    base.linked_req_ids,
    base.target_variant,
    distance
FROM VECTOR_SEARCH(
    TABLE `axiom-cloud-run.axiom_qa.test_cases_embeddings`,
    'embedding',
    (
        SELECT ml_generate_embedding_result AS query_vector
        FROM ML.GENERATE_EMBEDDING(
            MODEL `axiom-cloud-run.axiom_qa.text_embedding_004`,
            (SELECT 'Proximity boundary rapid unlock oscillation chatter at 2.0m' AS content)
        )
    ),
    top_k => 5,
    distance_type => 'COSINE'
);
*/
