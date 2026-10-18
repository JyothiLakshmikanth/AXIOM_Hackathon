#!/bin/bash
#
# AXIOM POC - GCP Cloud Run Deployment Script
# Deploys the Streamlit AXIOM POC application.
#
# Usage:
#   ./deploy.sh
#   ./deploy.sh prod us-central1
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENVIRONMENT="${1:-prod}"
REGION="${2:-us-central1}"

PROJECT_ID="$(gcloud config get-value project 2>/dev/null)"
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    echo "[ERROR] No GCP project configured."
    echo "Run: gcloud config set project axiom-510516"
    exit 1
fi

SERVICE_NAME="axiom-poc"
IMAGE_NAME="axiom-poc"
ARTIFACT_REPOSITORY="axiom-poc"

MEMORY="2Gi"
CPU="2"
TIMEOUT="3600"
MAX_INSTANCES="1"
MIN_INSTANCES="0"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    command -v gcloud >/dev/null 2>&1 || {
        log_error "gcloud CLI is not installed."
        exit 1
    }

    command -v docker >/dev/null 2>&1 || {
        log_error "Docker is not installed."
        exit 1
    }

    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "No active gcloud account. Run: gcloud auth login"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

ensure_apis() {
    log_info "Enabling required APIs..."

    gcloud services enable         run.googleapis.com         artifactregistry.googleapis.com         cloudbuild.googleapis.com         aiplatform.googleapis.com         secretmanager.googleapis.com         --project="$PROJECT_ID"         --quiet

    log_success "Required APIs are enabled"
}

ensure_artifact_registry() {
    log_info "Ensuring Artifact Registry repository exists..."

    if ! gcloud artifacts repositories describe "$ARTIFACT_REPOSITORY"         --location="$REGION"         --project="$PROJECT_ID" >/dev/null 2>&1; then

        gcloud artifacts repositories create "$ARTIFACT_REPOSITORY"             --repository-format=docker             --location="$REGION"             --description="AXIOM POC Docker images"             --project="$PROJECT_ID"             --quiet
    fi

    log_success "Artifact Registry repository: $ARTIFACT_REPOSITORY"
}

ensure_service_account() {
    local sa_name="axiom-orchestrator"
    local sa_email="${sa_name}@${PROJECT_ID}.iam.gserviceaccount.com"

    log_info "Ensuring service account exists: $sa_email"

    if ! gcloud iam service-accounts describe "$sa_email"         --project="$PROJECT_ID" >/dev/null 2>&1; then

        gcloud iam service-accounts create "$sa_name"             --display-name="AXIOM POC Cloud Run Service Account"             --project="$PROJECT_ID"
    fi

    local roles=(
        "roles/aiplatform.user"
        "roles/bigquery.dataEditor"
        "roles/bigquery.jobUser"
        "roles/datastore.user"
        "roles/logging.logWriter"
    )

    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID"             --member="serviceAccount:$sa_email"             --role="$role"             --quiet >/dev/null
    done

    log_success "Service account ready"
}

build_and_push() {
    local image="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPOSITORY}/${IMAGE_NAME}:${ENVIRONMENT}-$(date +%s)"

    log_info "Building Docker image..."
    docker build         --platform linux/amd64         -f Dockerfile         -t "$image"         .

    log_success "Docker image built: $image"

    log_info "Configuring Artifact Registry authentication..."
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

    log_info "Pushing Docker image..."
    docker push "$image"

    log_success "Docker image pushed"
    echo "$image"
}

deploy_to_cloud_run() {
    local image="$1"
    local service="${SERVICE_NAME}-${ENVIRONMENT}"
    local sa_email="axiom-orchestrator@${PROJECT_ID}.iam.gserviceaccount.com"

    # Read GEMINI_API_KEY from env or .env if present
    local gemini_key="${GEMINI_API_KEY:-}"
    if [ -z "$gemini_key" ] && [ -f ".env" ]; then
        gemini_key=$(grep -E '^GEMINI_API_KEY=' .env | head -n1 | cut -d'=' -f2- | tr -d '"\r' || true)
    fi

    local github_token="${GITHUB_TOKEN:-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}"
    local env_vars="ENVIRONMENT=${ENVIRONMENT},GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GCP_PROJECT=${PROJECT_ID},GCP_PROJECT_ID=${PROJECT_ID},VERTEX_AI_GEMINI_MODEL=gemini-1.5-flash-001,GITHUB_TOKEN=${github_token},NEO4J_URI=neo4j+s://fe6b9516.databases.neo4j.io,NEO4J_USERNAME=neo4j"
    if [ -n "$gemini_key" ]; then
        env_vars="${env_vars},GEMINI_API_KEY=${gemini_key},GOOGLE_API_KEY=${gemini_key}"
    fi

    gcloud run deploy "$service" \
        --image="$image" \
        --region="$REGION" \
        --platform=managed \
        --memory="$MEMORY" \
        --cpu="$CPU" \
        --timeout="$TIMEOUT" \
        --max-instances="$MAX_INSTANCES" \
        --min-instances="$MIN_INSTANCES" \
        --allow-unauthenticated \
        --session-affinity \
        --set-env-vars="$env_vars" \
        --service-account="$sa_email"

    log_success "Cloud Run deployment complete"
}

verify_deployment() {
    local service="${SERVICE_NAME}-${ENVIRONMENT}"

    log_info "Getting Cloud Run URL..."

    local url
    url="$(gcloud run services describe "$service"         --region="$REGION"         --format="value(status.url)")"

    if [ -z "$url" ]; then
        log_error "Could not retrieve Cloud Run URL"
        exit 1
    fi

    echo
    log_success "AXIOM POC URL: $url"
    echo

    log_info "Testing Streamlit health endpoint..."
    if curl -sSf "${url}/_stcore/health" >/dev/null; then
        log_success "Streamlit health check passed"
    else
        log_warn "Streamlit health check did not return 200 yet. Check Cloud Run logs."
    fi

    echo
    log_info "Useful commands:"
    echo "  gcloud run services logs read ${service} --region=${REGION} --limit=100"
    echo "  gcloud run services describe ${service} --region=${REGION}"
}

main() {
    log_info "Starting AXIOM POC deployment"
    log_info "Project: $PROJECT_ID"
    log_info "Region: $REGION"
    log_info "Service: ${SERVICE_NAME}-${ENVIRONMENT}"
    log_info "Repository: ${ARTIFACT_REPOSITORY}"

    check_prerequisites
    ensure_apis
    ensure_artifact_registry
    ensure_service_account

    IMAGE="$(build_and_push)"
    deploy_to_cloud_run "$IMAGE"
    verify_deployment

    log_success "AXIOM POC deployed successfully"
}

main "$@"
