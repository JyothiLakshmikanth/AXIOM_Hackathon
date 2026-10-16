# AXIOM Orchestrator - Quick Start Deployment to GCP Cloud Run

**Status:** ✅ Production-Ready  
**Version:** 4.0 (9-node unified LangGraph)  
**Deployment Time:** ~15-30 minutes  

---

## 🚀 5-Minute Setup

### Step 1: Prerequisites Check
```bash
# Verify tools installed
gcloud --version       # Need: >450.0.0
docker --version       # Need: >20.0.0
python --version       # Need: >=3.11
```

### Step 2: Authenticate with GCP
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
export PROJECT_ID=$(gcloud config get-value project)
```

### Step 3: Run Deployment Script
```bash
# Make script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh prod us-central1

# Deploy to staging (alternative)
./deploy.sh staging us-west1
```

**That's it!** The script will handle:
- ✅ Enable required APIs
- ✅ Create service account
- ✅ Configure IAM permissions
- ✅ Build Docker image
- ✅ Push to Google Container Registry
- ✅ Deploy to Cloud Run
- ✅ Verify health endpoint

---

## 🔍 What Gets Deployed

| Component | Details |
|-----------|---------|
| **Service** | `axiom-orchestrator-prod` |
| **Runtime** | Python 3.11 + FastAPI |
| **Memory** | 2 GB |
| **CPU** | 2 vCPU |
| **Timeout** | 3600 seconds (1 hour) |
| **Instances** | 1-10 (auto-scaling) |
| **Authentication** | Service account (no public access) |

---

## ✅ Verify Deployment

### Get Service URL
```bash
gcloud run services describe axiom-orchestrator-prod \
  --region us-central1 \
  --format="value(status.url)"
```

### Test Health Endpoint
```bash
TOKEN=$(gcloud auth print-identity-token)
SERVICE_URL=$(gcloud run services describe axiom-orchestrator-prod \
  --region us-central1 \
  --format="value(status.url)")

curl -H "Authorization: Bearer $TOKEN" \
  $SERVICE_URL/health
```

### Test Query Endpoint
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the project status?",
    "session_id": "test_1"
  }' \
  $SERVICE_URL/query
```

---

## 📊 Available Endpoints

```
GET  /health          — Health check
POST /query           — Process single query
POST /batch-query     — Process multiple queries
GET  /status          — Service status
GET  /metrics         — Performance metrics
GET  /info            — Service information
GET  /docs            — API documentation (Swagger)
GET  /redoc           — API docs (ReDoc)
```

---

## 🔧 Configuration

### Environment Variables (Set Automatically)
- `ENVIRONMENT` — prod | staging | dev
- `GOOGLE_CLOUD_PROJECT` — Your GCP project ID
- `PORT` — 8080 (Cloud Run default)

### Modify Deployment Parameters
Edit `deploy.sh` to change:
```bash
MEMORY="2Gi"           # Increase if needed
CPU="2"                # Adjust CPU cores
MAX_INSTANCES="10"     # Set max replicas
TIMEOUT="3600"         # Timeout in seconds
```

---

## 📈 Scaling

### Auto-Scaling is Enabled
- Minimum instances: 1
- Maximum instances: 10
- Auto-scales based on CPU and latency

### Manual Scaling
```bash
gcloud run services update axiom-orchestrator-prod \
  --region us-central1 \
  --min-instances 2 \
  --max-instances 20
```

---

## 🔍 Monitoring

### View Logs
```bash
# Stream logs (follow mode)
gcloud run logs read axiom-orchestrator-prod \
  --region us-central1 \
  --follow

# View last 50 logs
gcloud run logs read axiom-orchestrator-prod \
  --region us-central1 \
  --limit 50
```

### View Metrics Dashboard
```bash
# Open Cloud Console
gcloud run services describe axiom-orchestrator-prod \
  --region us-central1

# View in Cloud Console
# https://console.cloud.google.com/run/detail/us-central1/axiom-orchestrator-prod
```

---

## 🔄 Rollback to Previous Version

```bash
# List recent revisions
gcloud run revisions list \
  --service axiom-orchestrator-prod \
  --region us-central1 \
  --limit 5

# Switch traffic to previous revision
gcloud run services update-traffic axiom-orchestrator-prod \
  --region us-central1 \
  --to-revisions [REVISION_NAME]=100
```

---

## 🐛 Troubleshooting

### Service Won't Deploy
```bash
# Check service account exists and has permissions
gcloud iam service-accounts list | grep axiom-orchestrator

# Re-run deployment script with verbose output
./deploy.sh prod us-central1
```

### Health Check Failing
```bash
# Check if Gemini API is enabled
gcloud services list --enabled | grep aiplatform

# Check if Firestore exists
gcloud firestore databases list

# View detailed logs
gcloud run logs read axiom-orchestrator-prod \
  --region us-central1 \
  --limit 100
```

### Request Timeout
```bash
# Increase timeout (3600s = 1 hour)
gcloud run services update axiom-orchestrator-prod \
  --region us-central1 \
  --timeout 7200

# Check actual latencies
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 10 \
  --format json | grep latency
```

---

## 📋 Files Created

| File | Purpose |
|------|---------|
| **Dockerfile.new** | Multi-stage Docker build (optimized) |
| **deploy.sh** | Automated deployment script |
| **main.py** | FastAPI entry point |
| **requirements.txt** | Python dependencies |
| **cloudbuild.yaml** | CI/CD configuration |
| **.dockerignore** | Files to exclude from Docker build |

---

## 🎯 Next Steps

### Option 1: Streamlit UI (Optional)
```bash
streamlit run streamlit_app.py
```

### Option 2: Programmatic Access
```python
# Python client
import requests

url = "https://axiom-orchestrator-xxxxx.run.app/query"
headers = {"Authorization": f"Bearer {token}"}
data = {"query": "Your question here"}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Option 3: Terraform (Infrastructure as Code)
See `terraform/` directory for IaC setup (optional).

---

## 🔐 Security

### Service Account Permissions
Created with minimal required roles:
- `aiplatform.user` — For Gemini LLM
- `bigquery.dataEditor` — For data access
- `bigquery.jobUser` — For query execution
- `datastore.user` — For Firestore
- `logging.logWriter` — For Cloud Logging

### Public Access Disabled
- `--no-allow-unauthenticated` — Requires authentication
- Authentication via:
  - Service account key
  - gcloud identity token
  - Workload Identity (if using GKE)

---

## 💰 Cost Estimation

**Monthly cost** (estimated):
- Cloud Run compute: $2-5 (depending on usage)
- Firestore: <$1 (small dataset)
- BigQuery: <$1 (small queries)
- Gemini API: ~$2-10 (depends on token usage)

**Total: ~$5-20/month for low-to-medium usage**

---

## 📞 Support

### Common Commands
```bash
# Check service status
gcloud run services describe axiom-orchestrator-prod \
  --region us-central1

# Update service
gcloud run deploy axiom-orchestrator-prod \
  --update \
  --region us-central1

# Delete service
gcloud run services delete axiom-orchestrator-prod \
  --region us-central1
```

### Get Help
- Deployment script logs: check DEPLOYMENT_SUMMARY.txt
- Cloud Run logs: `gcloud run logs read axiom-orchestrator-prod`
- GCP Console: https://console.cloud.google.com/run

---

## ✨ Success Criteria

After deployment, verify:
- [x] Service is running on Cloud Run
- [x] Health endpoint returns `{"status":"healthy"}`
- [x] Query endpoint accepts POST requests
- [x] Logs appear in Cloud Logging
- [x] Service scales automatically

**If all pass: ✅ Deployment successful!**

---

**Ready to deploy?** Run:
```bash
chmod +x deploy.sh && ./deploy.sh prod us-central1
```

**Estimated time:** 15-30 minutes ⏱️  
**Status:** Production-ready 🚀
