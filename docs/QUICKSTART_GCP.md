# AXIOM Quick-Start: Deploy to GCP in 15 Minutes

## Prerequisites
- GCP account with $300 free credits (or paid billing enabled)
- `gcloud` CLI installed and authenticated: `gcloud auth login`
- Docker installed locally
- Project code cloned: `C:\New folder\builder_cup_hackk\AXIOM_Hackathon-main\AXIOM_Hackathon-main`

## 1. Create GCP Project (2 min)
```bash
# Set your project ID (must be globally unique)
export PROJECT_ID="axiom-hackathon-$(date +%s)"

# Create project
gcloud projects create $PROJECT_ID --name="AXIOM Multi-Agent Intelligence"
gcloud config set project $PROJECT_ID

# Enable billing (required for Cloud Run)
gcloud billing projects link $PROJECT_ID --billing-account=YOUR_BILLING_ID
```

## 2. Enable APIs (2 min)
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  logging.googleapis.com
```

## 3. Build & Push Docker Image (5 min)
```bash
# Navigate to project
cd "C:\New folder\builder_cup_hackk\AXIOM_Hackathon-main\AXIOM_Hackathon-main"

# Configure Docker auth
gcloud auth configure-docker

# Build image
docker build -t gcr.io/$PROJECT_ID/axiom:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/axiom:latest
```

## 4. Deploy to Cloud Run (3 min)
```bash
gcloud run deploy axiom \
  --image gcr.io/$PROJECT_ID/axiom:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600s \
  --allow-unauthenticated \
  --update-env-vars="LOG_LEVEL=INFO,DEPLOYMENT_ENV=gcp"
```

## 5. Test Your Deployment (3 min)
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe axiom --region us-central1 --format='value(status.url)')
echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl $SERVICE_URL/api/health

# Test chat endpoint
curl -X POST $SERVICE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the blast radius and defect triage for GH-ISSUE-107?",
    "session_id": "test_session_001",
    "target_master": "AXIOM-PM"
  }'
```

## Results
✅ AXIOM is now running on GCP Cloud Run  
✅ Publicly accessible API endpoint  
✅ Automatic scaling enabled  
✅ Cloud logging integrated  

## What You Get
- **2GB RAM, 2 CPUs** per instance
- **Auto-scaling** from 0 to 10 instances
- **1-hour timeout** for long-running RCA operations
- **Public HTTP API** at `https://axiom-XXXXX.run.app`
- **Cost**: ~$0.05/invocation (well under $300 monthly budget)

## Next Steps
1. **Add Firestore** for session persistence (optional):
   ```bash
   gcloud firestore databases create --type=datastore-mode --region=us-central1
   ```

2. **Connect Neo4j** for knowledge graphs (optional):
   - Create AuraDB instance: https://console.neo4j.io
   - Update Cloud Run env vars with Neo4j credentials

3. **Set Up Monitoring**:
   ```bash
   gcloud run services update axiom \
     --update-env-vars="ENABLE_METRICS=true,ENABLE_LOGGING=true"
   ```

4. **Enable CI/CD** (auto-deploy on git push):
   - Create `.github/workflows/deploy-gcp.yml` (template in `GCP_DEPLOYMENT_GUIDE.md`)
   - Connect GitHub repo to Cloud Build

## Cost Breakdown ($300 Budget)

| Service | Est. Monthly | Notes |
|---------|-------------|-------|
| Cloud Run | $50 | 2GB mem, 100k req/month |
| Firestore | $15 | 10GB storage |
| BigQuery | $6 | 1TB queried |
| Container Registry | $10 | 500GB stored |
| Cloud Logging | $15 | 50GB ingested |
| **Total** | **$96** | Remaining: $204 |

**Free Tier Included**: Cloud Monitoring, Cloud Trace, Cloud Profiler

## Troubleshooting

**Issue**: Image build fails  
→ Check Dockerfile is in root directory, run `docker build .` locally first

**Issue**: Cloud Run deployment fails  
→ Check services are enabled: `gcloud services list --enabled`

**Issue**: Health endpoint returns 500  
→ Check logs: `gcloud run logs read axiom --limit 50`

**Issue**: Slow responses  
→ Increase memory: `--memory 4Gi`, check logs for bottlenecks

## Useful Commands

```bash
# View deployment status
gcloud run services describe axiom --region us-central1

# Stream logs
gcloud run logs read axiom --follow

# Update environment variables
gcloud run services update axiom \
  --region us-central1 \
  --update-env-vars="KEY=VALUE"

# Delete service (stop billing)
gcloud run services delete axiom --region us-central1

# View container registry
gcloud container images list --project=$PROJECT_ID

# Get service metrics
gcloud monitoring timeseries list \
  --filter 'resource.type = "cloud_run_revision"'
```

## Key Files for Deployment

- **Dockerfile** - Container definition (Python 3.12)
- **app.py** - FastAPI server with health checks
- **cloudbuild.yaml** - CI/CD pipeline (if using Cloud Build)
- **GCP_DEPLOYMENT_GUIDE.md** - Full reference guide
- **REBRANDING_SUMMARY.md** - Rebranding details

## Architecture Deployed

```
┌─────────────────────────────────────────┐
│ Cloud Load Balancer (Global)            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Cloud Run (Serverless, Auto-scaling)    │
│ - AXIOM FastAPI Server                  │
│ - 2GB RAM, 2CPU per instance            │
│ - 0-10 instances (auto)                 │
└─────────────────────────────────────────┘
                    ↓
        ┌───────────────────┐
        │  Firestore        │  (Session memory)
        │  BigQuery         │  (Analytics)
        │  Neo4j AuraDB     │  (Knowledge graph)
        │  Cloud Logging    │  (Observability)
        └───────────────────┘
```

## Supported Queries (Examples)

```bash
# AXIOM-PM (Project Management) Query
curl -X POST $SERVICE_URL/api/chat \
  -d '{"query": "Sprint 4 is slipping by 18 story points, how should we replan?", "target_master": "AXIOM-PM"}'

# AXIOM-ENG (Engineering) Query
curl -X POST $SERVICE_URL/api/chat \
  -d '{"query": "Perform deep code RCA for proximity_controller.py", "target_master": "AXIOM-ENG"}'

# Auto-route (Intent detection)
curl -X POST $SERVICE_URL/api/chat \
  -d '{"query": "What is the blast radius for GH-ISSUE-107?"}'
```

---

**Status**: ✅ Ready to Deploy  
**Estimated Time**: 15-20 minutes  
**Cost**: $0-$5 for testing  
**Support**: Check logs with `gcloud run logs read axiom`
