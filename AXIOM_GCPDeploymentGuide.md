# AXIOM — GCP Deployment Guide

## 0. Deployment goal

Deploy AXIOM to Google Cloud Platform using:

- Cloud Run — Unified Streamlit Platform (streamlit_app.py) hosting the Risk Cockpit & Multi-Agent Orchestrator
- Artifact Registry — Docker images
- Vertex AI / Gemini — LLM inference
- Firestore — evidence/cache where required
- BigQuery — application structured data (axiom_data dataset: sprint, capacity, competency, PI planning)
- Secret Manager — sensitive credentials
- Cloud Logging — logs

### $300 credit strategy

The main costs to watch are:

1. Gemini / Vertex AI model calls
2. Cloud Run compute
3. BigQuery storage/query processing
4. Firestore reads/writes/storage
5. Other storage/build/network usage

API enablement and local configuration do not themselves create significant application usage.

---

# 1. Confirm the GCP project

```bash
gcloud projects list
```

Set the AXIOM project:

```bash
gcloud config set project axiom-510516
```

Verify:

```bash
gcloud config get-value project
```

Expected:

```text
axiom-510516
```

**Cost: $0**

---

# 2. Confirm authentication

```bash
gcloud auth list
```

Your intended Google account should show `ACTIVE: *`.

**Cost: $0**

---

# 3. Confirm billing

```bash
gcloud beta billing projects describe axiom-510516
```

Expected:

```text
billingEnabled: true
billingAccountName: billingAccounts/...
projectId: axiom-510516
```

If `billingEnabled` is false, stop and attach the correct billing account.

**Cost: $0**

---

# 4. Enable required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
```

Verify:

```bash
gcloud services list --enabled
```

Confirm at least:

```text
run.googleapis.com
artifactregistry.googleapis.com
cloudbuild.googleapis.com
aiplatform.googleapis.com
firestore.googleapis.com
bigquery.googleapis.com
secretmanager.googleapis.com
storage.googleapis.com
```

**Cost: $0 just for enabling APIs.**

---

# 5. Create Artifact Registry

Artifact Registry stores the Docker image used by Cloud Run.

Use one repository for AXIOM:

```bash
gcloud artifacts repositories create axiom   --repository-format=docker   --location=us-central1   --description="AXIOM Docker images"
```

Verify:

```bash
gcloud artifacts repositories list --location=us-central1
```

Expected:

```text
axiom    DOCKER    us-central1
```

### If you get BILLING_DISABLED

Run:

```bash
gcloud beta billing projects describe axiom-510516
```

If it says:

```text
billingEnabled: true
```

but Artifact Registry still reports `BILLING_DISABLED`, wait several minutes for billing propagation and retry.

Do not create another repository.

**Cost: low / potentially billable storage and operations.**

---

# 6. Go to the project root directory

All deployment files reside in the root repository directory:

```text
AXIOM_Hackathon/
    Dockerfile          # Unified Streamlit + Orchestrator container
    deploy.sh           # Automated Cloud Run deployment script
    streamlit_app.py    # Main UI (Risk Cockpit, Multi-Agent Chat, BigQuery Hub)
    requirements.txt    # Python dependencies
    cloudbuild.yaml     # Cloud Build CI/CD pipeline
    .dockerignore       # Build context exclusions
```

Navigate to the project root:

```bash
cd ~/AXIOM_Hackathon
ls
```

**Cost: $0**

---

# 7. Verify the application entry point and Dockerfile

Inspect the Dockerfile:

```bash
grep -n "FROM\|CMD\|ENTRYPOINT" Dockerfile
```

Expected output:
```text
2:FROM python:3.11-slim
31:    CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1
33:CMD ["sh", "-c", "exec streamlit run streamlit_app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false --server.enableCORS=false --server.enableXsrfProtection=false"]
```

The application runs **Streamlit (`streamlit_app.py`)** directly on Cloud Run.
The built-in health check endpoint is:
```text
/_stcore/health
```

**Cost: $0**

---

# 8. Review environment variables

Review the application's required configuration before building.

Typical values may include:

```text
GEMINI_MODEL
GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
QDRANT_URL
QDRANT_API_KEY
GITHUB_TOKEN
```

Do not put real passwords, API keys, tokens, or service-account JSON into the Dockerfile or Git repository.

Use Secret Manager for sensitive values.

**Cost: $0 for inspection/configuration. Secret Manager can have small usage charges.**

---

# 9. Create a dedicated Cloud Run service account

Create the service account:

```bash
gcloud iam service-accounts create axiom-orchestrator \
    --display-name="AXIOM Orchestrator"
```

Verify:

```bash
gcloud iam service-accounts list
```

### Grant Required IAM Roles
The service account needs access to Vertex AI (Gemini), BigQuery, and Cloud Logging:

```bash
PROJECT_ID="axiom-510516"
SA_EMAIL="axiom-orchestrator@${PROJECT_ID}.iam.gserviceaccount.com"

# Vertex AI / Gemini access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"

# BigQuery data reader and job runner
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/bigquery.jobUser"

# Cloud Logging
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/logging.logWriter"
```

**Cost: $0**

---

# 10. Configure Vertex AI / Gemini

AXIOM uses Gemini through Google Cloud / Vertex AI.

The Cloud Run service account should authenticate through Google Cloud IAM rather than embedding service-account JSON credentials in the container.

Use the model configured by the application. The documented configuration may include:

```text
GEMINI_MODEL=gemini-2.0-flash
```

**Cost: IMPORTANT — billable.**

Every model call can consume GCP credits. Because AXIOM uses router/master/agent components, one user query may generate multiple model calls.

Start testing with a small number of requests.

---

# 11. Configure Firestore

The AXIOM architecture uses Firestore for evidence/cache-related functionality.

Create the database only once and only after confirming the application's current configuration.

The deployment configuration uses:

```text
us-central1
```

**Cost: potentially billable.**

Main usage drivers include reads, writes, deletes, storage and network usage.

---

# 12. Configure BigQuery (Automated Data Loader)

The application uses the `axiom_data` BigQuery dataset for structured project tracking:
- `sprint_planning` (21 tasks, bugs, epics)
- `capacity_planning` (team capacity & 85% ceiling allocations)
- `competency_matrix` (64 skills across team members)
- `pi_planning` (PI-1 to PI-4 roadmaps & milestones)
- `test_cases` (Master ISO 29119 test store)

*(Note: Requirements data lives exclusively in the Neo4j Knowledge Graph and is not loaded into BigQuery).*

### Automated Population:
Run the loader script from the project root:

```bash
python data/load_to_bigquery.py --project axiom-510516
```

This creates the `axiom_data` dataset, generates BigQuery tables, and creates BigQuery ML text embeddings.

*(If BigQuery is empty or still populating, `agents/tools/bigquery_tools.py` automatically falls back to local CSVs without failing).*

**Cost: potentially billable storage and query charges.**

---

# 13. Configure Secret Manager

Store sensitive credentials in Secret Manager rather than source code.

Possible secrets include:

```text
NEO4J_PASSWORD
QDRANT_API_KEY
GITHUB_TOKEN
```

Do not commit secrets to Git.

**Cost: low / potentially billable.**

---

# 14. Authenticate Docker

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

**Cost: $0**

---

# 15. Build the Docker image

Use a versioned tag or `latest`:

```bash
docker build \
    -f Dockerfile \
    --platform linux/amd64 \
    -t us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1 \
    .
```

**Cost: generally $0 of GCP application credits when building in Cloud Shell/local Docker.**

---

# 16. Test the container before Cloud Run

Run locally in Cloud Shell:

```bash
docker run --rm \
    -p 8080:8080 \
    us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1
```

In another terminal, test Streamlit's health endpoint:

```bash
curl http://localhost:8080/_stcore/health
```

Expected output:
```text
ok
```

**Cost: $0 of Cloud Run credits.**

---

# 17. Push the image to Artifact Registry

```bash
docker push   us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1
```

**Cost: low / potentially billable storage and transfer.**

---

# 18. Deploy the Streamlit Platform to Cloud Run

Start conservatively because the project has approximately $300 of credits.

Recommended initial settings:
- Region: `us-central1`
- CPU: `2`
- Memory: `2Gi`
- Minimum instances: `0` (scales to zero when idle)
- Maximum instances: `1`

Deploy command:

```bash
gcloud run deploy axiom-orchestrator-prod \
    --image=us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1 \
    --region=us-central1 \
    --platform=managed \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=0 \
    --max-instances=1 \
    --allow-unauthenticated \
    --port=8080 \
    --service-account=axiom-orchestrator@axiom-510516.iam.gserviceaccount.com
```

**Cost: YES — billable compute.**

---

# 19. Get the Cloud Run URL & Test Health

```bash
gcloud run services describe axiom-orchestrator-prod \
    --region=us-central1 \
    --format="value(status.url)"
```

Save the returned URL. Open it in your web browser, or verify the health endpoint:

```bash
curl https://YOUR-CLOUD-RUN-URL/_stcore/health
```

Expected response: `ok`

**Cost: small Cloud Run usage.**

---

# 20. Check Cloud Run logs

```bash
gcloud run services logs read axiom-orchestrator-prod   --region=us-central1   --limit=50
```

Look for:

- startup/import errors
- missing environment variables
- authentication errors
- Vertex AI errors
- Firestore errors
- BigQuery errors
- Python exceptions

Fix these before deploying Streamlit.

---

# 21. Test ONE real AXIOM query

Do not immediately run hundreds of tests.

Start with one simple query, for example:

```text
What is the current project health?
```

Verify:

```text
User
 ↓
FastAPI
 ↓
LangGraph
 ↓
Router
 ↓
Master
 ↓
Specialized agent
 ↓
Tools
 ↓
Gemini
 ↓
Firestore / BigQuery if required
 ↓
Response
```

Record how many Gemini calls are generated for one query.

**Cost: YES.**

This is where Gemini usage begins.

---

# 22. Monitor the backend

After a few tests, check:

- Cloud Run usage
- Vertex AI/Gemini usage
- Firestore reads/writes
- BigQuery query processing
- Cloud Run logs

Do not increase the Cloud Run maximum until testing demonstrates that it is necessary.

---

# 23. Unified Architecture & Automated Deployment

AXIOM uses a unified container architecture:
```text
Browser (Executive PM / Engineer)
   ↓ (HTTPS)
Cloud Run [Streamlit Platform + Risk Cockpit]
   ↓ (In-Memory Internal StateGraph)
LangGraph (9-Node Cognitive Engine)
   ↓
AXIOM Masters (PM.ai + ENG.ai)
   ↓
Specialized Agents (Defect, Resource, Test, Security)
   ↓
Tools & Data (BigQuery axiom_data, Neo4j KG, Vertex AI Gemini)
```

There is **no need for a separate backend deployment** or `AXIOM_API_URL` configuration. The Streamlit container directly embeds the cognitive engine, protecting internal business logic from tampering while delivering responsive UI updates.

### One-Command Deployment Alternative:
You can also deploy in a single step using Cloud Build:

```bash
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_REGION=us-central1,_SERVICE_NAME=axiom-orchestrator,_ENVIRONMENT=prod
```

Or using the automated shell script:

```bash
chmod +x deploy.sh
./deploy.sh prod us-central1
```

---

# 26. Protect the $300 budget

Recommended alert thresholds:

```text
25%  = $75
50%  = $150
75%  = $225
90%  = $270
```

Important: budget alerts notify you; they are not a guaranteed automatic shutdown of every billable resource.

For cost control:

```text
Cloud Run:
    min = 0
    max = 1 initially

Gemini:
    control model calls
    avoid unnecessary repeated tests

BigQuery:
    avoid scanning unnecessary data

Firestore:
    avoid unnecessary repeated reads/writes

Artifact Registry:
    keep only required image versions
```

---

# 27. Updating the application later

Do NOT recreate Artifact Registry when the code changes.

Keep one repository:

```text
axiom
 ├── axiom:v1
 ├── axiom:v2
 ├── axiom:v3
 └── axiom:v4
```

Workflow:

```text
Fix code
   ↓
Build new image
   ↓
Test locally
   ↓
Push new tag
   ↓
Deploy new tag to Cloud Run
```

Example:

```bash
docker build \
    -f Dockerfile \
    --platform linux/amd64 \
    -t us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v2 \
    .

docker push us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v2
```

Then deploy `v2` to Cloud Run.

---

# 28. Final deployment checklist

```text
[x] GCP project: axiom-510516
[x] Billing enabled
[x] Required APIs enabled
[x] Artifact Registry repository created (axiom in us-central1)
[x] Dockerfile verified (Streamlit + Risk Cockpit)
[x] requirements.txt verified (streamlit>=1.30.0)
[ ] Service account created (axiom-orchestrator)
[ ] IAM permissions configured (Vertex AI, BigQuery, Logging)
[ ] BigQuery populated (python data/load_to_bigquery.py)
[ ] Docker image built & pushed
[ ] Cloud Run deployed (axiom-orchestrator-prod)
[ ] Health endpoint verified (/_stcore/health)
[ ] Risk Cockpit & Multi-Agent query verified
[ ] Budget alerts configured
```

## Current position

Based on the deployment work already completed:

```text
GCP project          ✅
Billing              ✅
Authentication       ✅
APIs                 ✅
Artifact Registry    ✅
Service Account      ⏳ (Next: Step 9)
BigQuery Data        ⏳ (Next: Step 12)
Docker build & push  ⏳ (Next: Step 15)
Cloud Run            ⏳ (Next: Step 18)
```

**Next action in Cloud Shell:**

```bash
gcloud iam service-accounts create axiom-orchestrator \
    --display-name="AXIOM Orchestrator"
```
