"""
GCP Client for AXIOM — Singleton wrapper for Google Cloud services.
Provides unified interface to Vertex AI (Gemini), BigQuery, and Firestore.
Handles authentication, error recovery, logging, and retry logic.
"""

import logging
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger("axiom.orchestrator.gcp_client")

# Module-level singleton instance
_gcp_instance: Optional["GCPClient"] = None


class GCPClient:
    """
    Singleton client for Google Cloud services integration.

    Manages connections to:
    - Vertex AI Generative Models (Gemini)
    - BigQuery for structured data queries
    - Firestore for runtime state and evidence caching

    Provides retry logic, error handling, and comprehensive logging.
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self, project_id: str, region: str = "us-central1"):
        """
        Initialize GCP client with project and region configuration.

        Args:
            project_id: Google Cloud project ID
            region: GCP region for Vertex AI (default: us-central1)

        Raises:
            ValueError: If project_id is empty or invalid
        """
        if not project_id or not isinstance(project_id, str):
            raise ValueError(f"Invalid project_id: {project_id}")

        self.project_id = project_id
        self.region = region

        logger.info(f"Initializing GCPClient for project={project_id}, region={region}")

        # Lazy initialization of service clients (only when first used)
        self._gemini_model = None
        self._bq_client = None
        self._firestore_client = None

        logger.debug(f"GCPClient initialized (services will be lazy-loaded on first use)")

    def call_gemini(
        self, system_prompt: str, user_input: str, temperature: float = 0.7
    ) -> str:
        """
        Call Vertex AI Gemini model with system and user prompts.

        Uses gemini-2.0-flash-001 model with streaming support.
        Implements retry logic with exponential backoff on transient failures.

        Args:
            system_prompt: System context and instructions for the model
            user_input: User query or task input
            temperature: Sampling temperature (0.0 to 1.0), default 0.7

        Returns:
            Complete response text from Gemini model

        Raises:
            RuntimeError: If all retries exhausted or authentication fails
            ValueError: If prompts are invalid (empty, too long)
        """
        if not system_prompt or not isinstance(system_prompt, str):
            raise ValueError("system_prompt must be a non-empty string")
        if not user_input or not isinstance(user_input, str):
            raise ValueError("user_input must be a non-empty string")
        if not (0.0 <= temperature <= 1.0):
            raise ValueError(f"temperature must be between 0.0 and 1.0, got {temperature}")

        logger.debug(f"call_gemini: system_prompt_len={len(system_prompt)}, user_input_len={len(user_input)}, temp={temperature}")

        for attempt in range(self.MAX_RETRIES):
            try:
                # Lazy load Gemini model on first use
                if self._gemini_model is None:
                    self._init_gemini()

                # Prepare message with system prompt
                full_prompt = f"{system_prompt}\n\n{user_input}"

                logger.debug(f"Calling Gemini (attempt {attempt + 1}/{self.MAX_RETRIES})")

                # Call Gemini via vertexai API
                response = self._gemini_model.generate_content(
                    contents=full_prompt,
                    generation_config={
                        "temperature": temperature,
                        "top_k": 40,
                        "top_p": 0.95,
                        "max_output_tokens": 8192,
                    },
                    stream=False,
                )

                result_text = response.text if response else ""

                if not result_text:
                    logger.warning("Gemini returned empty response")
                    raise RuntimeError("Empty response from Gemini")

                logger.info(f"Gemini call succeeded: {len(result_text)} chars returned")
                return result_text

            except Exception as e:
                logger.warning(f"Gemini call failed (attempt {attempt + 1}): {e}")

                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.MAX_RETRIES} Gemini retries exhausted")
                    raise RuntimeError(f"Gemini call failed after {self.MAX_RETRIES} attempts: {e}") from e

        raise RuntimeError("Unexpected exit from Gemini call loop")

    def query_bigquery(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query against BigQuery and return results as list of dictionaries.

        Implements retry logic for transient failures (network, quota).
        Returns empty list if query returns no rows.

        Args:
            sql: SQL query string to execute

        Returns:
            List of row dictionaries from query result

        Raises:
            RuntimeError: If all retries exhausted or query validation fails
            ValueError: If SQL is invalid (empty, None)
        """
        if not sql or not isinstance(sql, str):
            raise ValueError("sql must be a non-empty string")

        logger.debug(f"query_bigquery: sql_len={len(sql)}")

        for attempt in range(self.MAX_RETRIES):
            try:
                # Lazy load BigQuery client on first use
                if self._bq_client is None:
                    self._init_bigquery()

                logger.debug(f"Executing BigQuery query (attempt {attempt + 1}/{self.MAX_RETRIES})")

                # Execute query
                query_job = self._bq_client.query(sql)
                results = query_job.result()

                # Convert to list of dicts
                rows = [dict(row) for row in results]

                logger.info(f"BigQuery query succeeded: {len(rows)} rows returned")
                return rows

            except Exception as e:
                logger.warning(f"BigQuery query failed (attempt {attempt + 1}): {e}")

                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.MAX_RETRIES} BigQuery retries exhausted")
                    raise RuntimeError(f"BigQuery query failed after {self.MAX_RETRIES} attempts: {e}") from e

        raise RuntimeError("Unexpected exit from BigQuery query loop")

    def get_firestore(self, doc_path: str) -> Dict[str, Any]:
        """
        Retrieve document from Firestore by path.

        Path format: "collections/collection_id/document_id" or
                     "collections/col1/doc1/col2/doc2"

        Returns empty dict if document does not exist.

        Args:
            doc_path: Firestore document path

        Returns:
            Document data as dictionary, or empty dict if not found

        Raises:
            RuntimeError: If all retries exhausted or Firestore unavailable
            ValueError: If doc_path is invalid (empty, None)
        """
        if not doc_path or not isinstance(doc_path, str):
            raise ValueError("doc_path must be a non-empty string")

        logger.debug(f"get_firestore: doc_path={doc_path}")

        for attempt in range(self.MAX_RETRIES):
            try:
                # Lazy load Firestore client on first use
                if self._firestore_client is None:
                    self._init_firestore()

                logger.debug(f"Fetching Firestore doc (attempt {attempt + 1}/{self.MAX_RETRIES})")

                # Get document
                doc = self._firestore_client.document(doc_path).get()

                if not doc.exists:
                    logger.debug(f"Document not found: {doc_path}")
                    return {}

                data = doc.to_dict() or {}
                logger.info(f"Firestore get succeeded: {doc_path} ({len(data)} fields)")
                return data

            except Exception as e:
                logger.warning(f"Firestore get failed (attempt {attempt + 1}): {e}")

                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.MAX_RETRIES} Firestore get retries exhausted")
                    raise RuntimeError(f"Firestore get failed after {self.MAX_RETRIES} attempts: {e}") from e

        raise RuntimeError("Unexpected exit from Firestore get loop")

    def set_firestore(self, doc_path: str, data: Dict[str, Any]) -> None:
        """
        Write document to Firestore at specified path, creating or updating.

        Uses merge=True to preserve existing fields not in the update.

        Args:
            doc_path: Firestore document path
            data: Document data dictionary to write

        Raises:
            RuntimeError: If all retries exhausted or Firestore unavailable
            ValueError: If doc_path or data is invalid
        """
        if not doc_path or not isinstance(doc_path, str):
            raise ValueError("doc_path must be a non-empty string")
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        logger.debug(f"set_firestore: doc_path={doc_path}, data_keys={list(data.keys())}")

        for attempt in range(self.MAX_RETRIES):
            try:
                # Lazy load Firestore client on first use
                if self._firestore_client is None:
                    self._init_firestore()

                logger.debug(f"Writing to Firestore (attempt {attempt + 1}/{self.MAX_RETRIES})")

                # Set document (merge=True preserves existing fields)
                self._firestore_client.document(doc_path).set(data, merge=True)

                logger.info(f"Firestore set succeeded: {doc_path} ({len(data)} fields)")
                return

            except Exception as e:
                logger.warning(f"Firestore set failed (attempt {attempt + 1}): {e}")

                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.MAX_RETRIES} Firestore set retries exhausted")
                    raise RuntimeError(f"Firestore set failed after {self.MAX_RETRIES} attempts: {e}") from e

        raise RuntimeError("Unexpected exit from Firestore set loop")

    def _init_gemini(self) -> None:
        """
        Lazy initialization of Vertex AI Generative Model.

        Called on first use of call_gemini() to minimize startup overhead.
        """
        try:
            import os
            from vertexai.generative_models import GenerativeModel

            model_name = os.getenv("VERTEX_AI_GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
            self._gemini_model = GenerativeModel(model_name)
            logger.info(f"Vertex AI Gemini model initialized: {model_name}")

        except ImportError as e:
            logger.error(f"Failed to import vertexai: {e}")
            raise RuntimeError("vertexai SDK not installed") from e
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise RuntimeError(f"Gemini initialization failed: {e}") from e

    def _init_bigquery(self) -> None:
        """
        Lazy initialization of BigQuery client.

        Called on first use of query_bigquery() to minimize startup overhead.
        """
        try:
            logger.debug("Initializing BigQuery client")
            from google.cloud import bigquery

            self._bq_client = bigquery.Client(project=self.project_id)
            logger.info("BigQuery client initialized")

        except ImportError as e:
            logger.error(f"Failed to import google.cloud.bigquery: {e}")
            raise RuntimeError("google-cloud-bigquery SDK not installed") from e
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise RuntimeError(f"BigQuery initialization failed: {e}") from e

    def _init_firestore(self) -> None:
        """
        Lazy initialization of Firestore client.

        Called on first use of get_firestore() or set_firestore() to minimize startup overhead.
        """
        try:
            logger.debug("Initializing Firestore client")
            from google.cloud import firestore

            self._firestore_client = firestore.Client(project=self.project_id)
            logger.info("Firestore client initialized")

        except ImportError as e:
            logger.error(f"Failed to import google.cloud.firestore: {e}")
            raise RuntimeError("google-cloud-firestore SDK not installed") from e
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise RuntimeError(f"Firestore initialization failed: {e}") from e


def get_gcp_client(project_id: str = None, region: str = "us-central1") -> GCPClient:
    """
    Get or create module-level GCPClient singleton.

    If called with arguments, initializes new client (overwrites existing).
    If called without arguments, returns existing client (must have been initialized).

    Args:
        project_id: Google Cloud project ID (required on first call)
        region: GCP region for Vertex AI (default: us-central1)

    Returns:
        GCPClient singleton instance

    Raises:
        RuntimeError: If no project_id provided and client not yet initialized
    """
    global _gcp_instance

    if project_id is not None:
        # Initialize or reinitialize
        logger.info(f"Creating new GCPClient instance for project={project_id}")
        _gcp_instance = GCPClient(project_id=project_id, region=region)

    elif _gcp_instance is None:
        raise RuntimeError(
            "GCPClient not initialized. Call get_gcp_client(project_id='...') first."
        )

    return _gcp_instance
