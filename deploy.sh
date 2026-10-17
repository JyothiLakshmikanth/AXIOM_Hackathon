#!/bin/bash
#
# AXIOM Orchestrator - GCP Cloud Run Deployment Script
# Deploys unified 9-node LangGraph with PM.ai + ENG.ai masters
#
# Usage:
#   ./deploy.sh [environment] [region]
#   ./deploy.sh prod us-central1
#   ./deploy.sh staging us-west1

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Deployment parameters
ENVIRONMENT="${1:-prod}"
REGION="${2:-us-central1}"
SERVICE_NAME="axiom-orchestrator"
IMAGE_NAME="axiom-orchestrator"
ARTIFACT_REPOSITORY="axiom"
MEMORY="2Gi"
CPU="2"
TIMEOUT="3600"
MAX_INSTANCES="1"
MIN_INSTANCES="0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

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

    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not installed. Install from: https://cloud.google.com/sdk/install"
        exit 1
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not installed. Install from: https://docs.docker.com/install/"
        exit 1
    fi

    # Check gcloud authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

get_project_id() {
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        log_error "No GCP project configured. Run: gcloud config set project PROJECT_ID"
        exit 1
    fi
    echo "$PROJECT_ID"
}

validate_config() {
    log_info "Validating configuration..."

    PROJECT_ID=$(get_project_id)
    log_info "  Project ID: $PROJECT_ID"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Region: $REGION"
    log_info "  Service: $SERVICE_NAME-$ENVIRONMENT"
    log_info "  Memory: $MEMORY"
    log_info "  CPU: $CPU"
    log_info "  Timeout: ${TIMEOUT}s"

    # Validate region
    VALID_REGIONS=$(gcloud compute regions list --format="value(name)")
    if ! echo "$VALID_REGIONS" | grep -q "^$REGION$"; then
        log_error "Invalid region: $REGION"
        exit 1
    fi

    log_success "Configuration validated"
}

check_environment_variables() {
    log_info "Checking required environment variables..."

    REQUIRED_VARS=(
        "GOOGLE_CLOUD_PROJECT"
        "GOOGLE_APPLICATION_CREDENTIALS"
    )

    MISSING_VARS=()
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var:-}" ]; then
            MISSING_VARS+=("$var")
        fi
    done

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        log_warn "Missing environment variables: ${MISSING_VARS[*]}"
        log_info "These will be set in Cloud Run via --set-env-vars"
    else
        log_success "Environment variables configured"
    fi
}

build_docker_image() {
    log_info "Building Docker image..."

    PROJECT_ID=$(get_project_id)
    FULL_IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPOSITORY/$IMAGE_NAME:$ENVIRONMENT-$(date +%s)"

    if ! docker build -f Dockerfile -t "$FULL_IMAGE_NAME" \
        --build-arg ENVIRONMENT=$ENVIRONMENT \
        --platform linux/amd64 \
        .; then
        log_error "Docker build failed"
        exit 1
    fi

    log_success "Docker image built: $FULL_IMAGE_NAME"
    echo "$FULL_IMAGE_NAME"
}

ensure_artifact_registry() {
    log_info "Ensuring Artifact Registry repository exists..."

    PROJECT_ID=$(get_project_id)
    gcloud services enable artifactregistry.googleapis.com --project "$PROJECT_ID" --quiet

    if ! gcloud artifacts repositories describe "$ARTIFACT_REPOSITORY" \
        --location "$REGION" --project "$PROJECT_ID" &> /dev/null; then
        gcloud artifacts repositories create "$ARTIFACT_REPOSITORY" \
            --repository-format docker \
            --location "$REGION" \
            --description "AXIOM container images" \
            --project "$PROJECT_ID" \
            --quiet
    fi

    log_success "Artifact Registry repository is ready"
}

push_to_artifact_registry() {
    log_info "Pushing image to Artifact Registry..."

    FULL_IMAGE_NAME=$1

    gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

    if ! docker push "$FULL_IMAGE_NAME"; then
        log_error "Failed to push image to Artifact Registry"
        exit 1
    fi

    log_success "Image pushed to GCR: $FULL_IMAGE_NAME"
}

deploy_to_cloud_run() {
    log_info "Deploying to Cloud Run..."

    PROJECT_ID=$(get_project_id)
    FULL_IMAGE_NAME=$1
    SERVICE_NAME_FULL="$SERVICE_NAME-$ENVIRONMENT"

    # gcloud run deploy creates the service when needed and updates it otherwise.
    gcloud run deploy "$SERVICE_NAME_FULL" \
        --image "$FULL_IMAGE_NAME" \
        --region "$REGION" \
        --platform managed \
        --memory "$MEMORY" \
        --cpu "$CPU" \
        --timeout "$TIMEOUT" \
        --max-instances "$MAX_INSTANCES" \
        --min-instances "$MIN_INSTANCES" \
        --no-allow-unauthenticated \
        --set-env-vars "ENVIRONMENT=$ENVIRONMENT,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
        --service-account "axiom-orchestrator@$PROJECT_ID.iam.gserviceaccount.com" \
        --labels "service=axiom,environment=$ENVIRONMENT,managed-by=deploy-script" \
        --revision-suffix="$(date +%s)"

    log_success "Cloud Run deployment complete"
}

verify_deployment() {
    log_info "Verifying deployment..."

    PROJECT_ID=$(get_project_id)
    SERVICE_NAME_FULL="$SERVICE_NAME-$ENVIRONMENT"

    # Get service details
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME_FULL" \
        --region "$REGION" \
        --format="value(status.url)")

    if [ -z "$SERVICE_URL" ]; then
        log_error "Failed to retrieve service URL"
        exit 1
    fi

    log_success "Service URL: $SERVICE_URL"

    # Test health endpoint
    log_info "Testing health endpoint..."
    sleep 10  # Wait for service to be ready

    if curl -s -f -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$SERVICE_URL/_stcore/health" > /dev/null || curl -s -f -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$SERVICE_URL/health" > /dev/null; then
        log_success "Health check passed"
    else
        log_warn "Health check failed (service may still be warming up)"
    fi
}

create_iam_service_account() {
    log_info "Setting up IAM service account..."

    PROJECT_ID=$(get_project_id)
    SA_NAME="axiom-orchestrator"
    SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

    # Check if service account exists
    if ! gcloud iam service-accounts describe "$SA_EMAIL" &> /dev/null; then
        log_info "Creating service account: $SA_EMAIL"
        gcloud iam service-accounts create "$SA_NAME" \
            --display-name="AXIOM Orchestrator Service Account"
    else
        log_info "Service account already exists: $SA_EMAIL"
    fi

    # Grant required roles
    ROLES=(
        "roles/aiplatform.user"
        "roles/bigquery.dataEditor"
        "roles/bigquery.jobUser"
        "roles/datastore.user"
        "roles/logging.logWriter"
        "roles/cloudtrace.agent"
    )

    for role in "${ROLES[@]}"; do
        log_info "Granting role: $role"
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SA_EMAIL" \
            --role="$role" \
            --quiet
    done

    log_success "IAM setup complete"
}

setup_firestore() {
    log_info "Ensuring Firestore database exists..."

    PROJECT_ID=$(get_project_id)

    # Check if Firestore exists
    if ! gcloud firestore databases list --filter="type:FIRESTORE" &> /dev/null; then
        log_info "Creating Firestore database..."
        gcloud firestore databases create \
            --region="us-central1" \
            --type=firestore-native
    else
        log_info "Firestore database already exists"
    fi

    log_success "Firestore setup complete"
}

setup_bigquery() {
    log_info "Ensuring BigQuery datasets exist..."

    PROJECT_ID=$(get_project_id)
    DATASETS=("axiom_data" "axiom_cache" "axiom_logs")

    for dataset in "${DATASETS[@]}"; do
        if ! bq ls -d "$dataset" &> /dev/null; then
            log_info "Creating BigQuery dataset: $dataset"
            bq mk --dataset "$PROJECT_ID:$dataset"
        else
            log_info "BigQuery dataset already exists: $dataset"
        fi
    done

    log_success "BigQuery setup complete"
}

create_deployment_summary() {
    log_info "Creating deployment summary..."

    PROJECT_ID=$(get_project_id)
    SERVICE_NAME_FULL="$SERVICE_NAME-$ENVIRONMENT"
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME_FULL" \
        --region "$REGION" \
        --format="value(status.url)")

    SUMMARY_FILE="DEPLOYMENT_SUMMARY.txt"

    cat > "$SUMMARY_FILE" << EOF
================================================================================
AXIOM ORCHESTRATOR - DEPLOYMENT SUMMARY
================================================================================

Deployment Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Environment: $ENVIRONMENT
Region: $REGION

================================================================================
SERVICE DETAILS
================================================================================

Service Name: $SERVICE_NAME_FULL
Project ID: $PROJECT_ID
Service URL: $SERVICE_URL

Memory: $MEMORY
CPU: $CPU
Timeout: ${TIMEOUT}s
Max Instances: $MAX_INSTANCES
Min Instances: $MIN_INSTANCES

================================================================================
ARCHITECTURE
================================================================================

✅ 9-Node Unified LangGraph
✅ PM.ai (AXIOM-PM) Master
✅ ENG.ai (AXIOM-ENG) Master
✅ GCP Gemini 2.0 Flash Integration
✅ Firestore Evidence Cache
✅ BigQuery Data Access
✅ LLM-Driven Intent Router
✅ Intelligent Agent Selection
✅ Cross-Master Handoff
✅ HITL Checkpoint

================================================================================
NEXT STEPS
================================================================================

1. Test the service:
   curl -H "Authorization: Bearer \$(gcloud auth print-identity-token)" \\
     $SERVICE_URL/query

2. View logs:
   gcloud run logs read $SERVICE_NAME_FULL --region $REGION --limit 50

3. Monitor metrics:
   gcloud monitoring dashboards create --config-from-file=monitoring.yaml

4. Update if needed:
   ./deploy.sh $ENVIRONMENT $REGION

5. Rollback to previous version:
   gcloud run services update-traffic $SERVICE_NAME_FULL \\
     --to-revisions REVISION_NAME=50

================================================================================
SUPPORT
================================================================================

View service logs: gcloud run logs read $SERVICE_NAME_FULL --region $REGION
View service details: gcloud run services describe $SERVICE_NAME_FULL --region $REGION
Update service: gcloud run deploy $SERVICE_NAME_FULL --region $REGION --image IMAGE_URL
Delete service: gcloud run services delete $SERVICE_NAME_FULL --region $REGION

================================================================================
EOF

    log_success "Deployment summary created: $SUMMARY_FILE"
    cat "$SUMMARY_FILE"
}

# ============================================================================
# MAIN DEPLOYMENT FLOW
# ============================================================================

main() {
    log_info "╔════════════════════════════════════════════════════════════════╗"
    log_info "║           AXIOM ORCHESTRATOR - GCP CLOUD RUN DEPLOY            ║"
    log_info "╚════════════════════════════════════════════════════════════════╝"
    log_info ""

    # Pre-deployment checks
    check_prerequisites
    validate_config
    check_environment_variables

    # Infrastructure setup
    create_iam_service_account
    setup_firestore
    setup_bigquery
    ensure_artifact_registry

    # Container build and push
    FULL_IMAGE_NAME=$(build_docker_image)
    push_to_artifact_registry "$FULL_IMAGE_NAME"

    # Deploy to Cloud Run
    deploy_to_cloud_run "$FULL_IMAGE_NAME"

    # Verification
    verify_deployment

    # Summary
    create_deployment_summary

    log_info ""
    log_success "╔════════════════════════════════════════════════════════════════╗"
    log_success "║        AXIOM ORCHESTRATOR DEPLOYED SUCCESSFULLY! 🚀            ║"
    log_success "╚════════════════════════════════════════════════════════════════╝"
}

# Execute main function
main "$@"
