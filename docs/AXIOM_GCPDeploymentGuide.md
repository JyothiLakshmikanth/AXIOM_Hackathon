# AXIOM — GCP Deployment Guide

## 0. Deployment goal

Deploy AXIOM to Google Cloud Platform using:

- Cloud Run — FastAPI backend and later Streamlit frontend
- Artifact Registry — Docker images
- Vertex AI / Gemini — LLM inference
- Firestore — evidence/cache where required
- BigQuery — application data/cache/log datasets where required
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

# 6. Go to the deployment directory

The project deployment files should include:

```text
deployment/
    Dockerfile.new
    deploy.sh
    main.py
    requirements.txt
    cloudbuild.yaml
    .dockerignore
```

Go to the project and deployment directory:

```bash
cd ~/AXIOM_Hackathon-main
cd deployment
ls
```

If your project directory has a different name, use the actual directory.

**Cost: $0**

---

# 7. Verify the application entry point and Dockerfile

There are multiple Dockerfiles in the project, so do not blindly build one.

Inspect the intended Dockerfile:

```bash
grep -n "FROM\|CMD\|ENTRYPOINT\|WORKERS" Dockerfile.new
```

Inspect the FastAPI application:

```bash
grep -n "FastAPI" main.py
```

Check health endpoints:

```bash
grep -n "health" main.py
```

The current project documentation identifies `main.py` as the FastAPI entry point and `Dockerfile.new` as a deployment file.

Do not assume `/health` or `/api/health` until the code confirms it.

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

Example:

```bash
gcloud iam service-accounts create axiom-orchestrator   --display-name="AXIOM Orchestrator"
```

Verify:

```bash
gcloud iam service-accounts list
```

The application may require access to Vertex AI, BigQuery, Firestore and logging. Grant only the roles actually required.

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

# 12. Configure BigQuery

The deployment configuration expects:

```text
axiom_data
axiom_cache
axiom_logs
```

Create them only if the application requires them.

BigQuery cost is driven mainly by storage and data processed by queries.

Avoid unnecessary queries such as:

```sql
SELECT * FROM large_table;
```

when only a few columns/rows are needed.

Prefer filtered queries, selected columns and caching where appropriate.

**Cost: potentially billable.**

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

Use a versioned tag while debugging.

Example:

```bash
docker build   -f Dockerfile.new   --platform linux/amd64   -t us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1   .
```

If the confirmed Dockerfile or build context differs, use the paths confirmed in Step 7.

**Cost: generally $0 of GCP application credits when building in Cloud Shell/local Docker.**

If the build fails, fix the code/Dockerfile and rebuild. Do not create another Artifact Registry repository.

---

# 16. Test the container before Cloud Run

Run:

```bash
docker run --rm   -p 8080:8080   us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1
```

In another terminal, test the confirmed health endpoint. For example:

```bash
curl http://localhost:8080/health
```

Use the actual endpoint found in Step 7.

**Cost: $0 of Cloud Run credits.**

---

# 17. Push the image to Artifact Registry

```bash
docker push   us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1
```

**Cost: low / potentially billable storage and transfer.**

---

# 18. Deploy the FastAPI backend to Cloud Run

Start conservatively because the project has approximately $300 of credits.

Recommended initial settings:

```text
Region:          us-central1
CPU:             1–2
Memory:          2 GiB
Minimum:         0
Maximum:         1
```

Example:

```bash
gcloud run deploy axiom-orchestrator-prod   --image=us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v1   --region=us-central1   --platform=managed   --memory=2Gi   --cpu=2   --min-instances=0   --max-instances=1   --port=8080
```

Add the confirmed service account, secrets and environment variables after checking their exact names.

**Cost: YES — billable compute.**

`min-instances=0` allows the service to scale down when unused. Keep `max-instances=1` initially to prevent unexpected scaling during development.

---

# 19. Get the Cloud Run URL

```bash
gcloud run services describe axiom-orchestrator-prod   --region=us-central1   --format="value(status.url)"
```

Save the returned URL.

Test the confirmed health endpoint:

```bash
curl https://YOUR-CLOUD-RUN-URL/health
```

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

# 23. Deploy Streamlit after the backend works

Deploy the Streamlit frontend only after FastAPI is stable.

Architecture:

```text
Browser
   |
   v
Streamlit Cloud Run
   |
   | HTTPS
   v
FastAPI Cloud Run
   |
   v
LangGraph
   |
   v
AXIOM agents
```

Initially use:

```text
min instances = 0
max instances = 1
```

**Cost: YES — additional Cloud Run usage.**

---

# 24. Configure the Streamlit backend URL

The Streamlit application should point to the deployed FastAPI URL, for example:

```text
AXIOM_API_URL=https://<fastapi-cloud-run-url>
```

Use environment variables/secrets rather than hard-coding credentials.

---

# 25. End-to-end test

Test:

```text
Browser
  ↓
Streamlit
  ↓
FastAPI
  ↓
LangGraph
  ↓
Master
  ↓
Specialized Agent
  ↓
Tools
  ↓
Gemini
  ↓
Firestore / BigQuery
```

Test one query at a time while monitoring logs and billing.

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
docker build   -f Dockerfile.new   --platform linux/amd64   -t us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v2   .

docker push   us-central1-docker.pkg.dev/axiom-510516/axiom/axiom:v2
```

Then deploy `v2` to Cloud Run.

---

# 28. Final deployment checklist

```text
[ ] GCP project: axiom-510516
[ ] Billing enabled
[ ] Required APIs enabled
[ ] Artifact Registry repository created
[ ] Correct Dockerfile identified
[ ] main.py verified
[ ] requirements.txt verified
[ ] Environment variables reviewed
[ ] Service account created
[ ] IAM permissions configured
[ ] Vertex AI/Gemini configured
[ ] Firestore configured if required
[ ] BigQuery configured if required
[ ] Secrets stored in Secret Manager
[ ] Docker authentication configured
[ ] Docker image built
[ ] Container tested locally
[ ] Image pushed to Artifact Registry
[ ] FastAPI deployed to Cloud Run
[ ] Health endpoint tested
[ ] Cloud Run logs checked
[ ] One AXIOM query tested
[ ] Gemini usage checked
[ ] Streamlit deployed
[ ] End-to-end query tested
[ ] Budget alerts configured
```

## Current position

Based on the deployment work already completed:

```text
GCP project          ✅
Billing              ✅
Authentication       ✅
APIs                 ✅
Artifact Registry    ⏳
Docker build         ⏳
Cloud Run            ⏳
Gemini               ⏳
Firestore            ⏳
BigQuery             ⏳
Streamlit            ⏳
```

**Next action:**

```bash
gcloud artifacts repositories create axiom   --repository-format=docker   --location=us-central1   --description="AXIOM Docker images"
```

If it succeeds, stop and move to Dockerfile/application verification before building or deploying anything.
