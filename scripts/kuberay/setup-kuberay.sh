#!/usr/bin/env bash
# ==============================================================================
# scripts/kuberay/setup-kuberay.sh
# Lifecycle script for multi-node KinD and KubeRay cluster testing.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLUSTER_NAME="${CLUSTER_NAME:-raylings-kind}"
RAY_CLUSTER_NAME="${RAY_CLUSTER_NAME:-raylings-cluster}"
NAMESPACE="${NAMESPACE:-default}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

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
    local missing=0
    for cmd in kind kubectl helm docker; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "Required CLI tool '$cmd' is not installed or not in PATH."
            missing=1
        fi
    done

    if [ "$missing" -eq 1 ]; then
        log_error "Please install missing prerequisites before proceeding."
        exit 1
    fi

    if ! docker info &>/dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi

    log_success "All prerequisites are satisfied."
}

cluster_up() {
    check_prerequisites

    # 1. Create KinD cluster if it doesn't exist
    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        log_info "KinD cluster '${CLUSTER_NAME}' already exists. Skipping creation."
    else
        log_info "Creating KinD cluster '${CLUSTER_NAME}' using ${SCRIPT_DIR}/kind-config.yaml..."
        kind create cluster --name "${CLUSTER_NAME}" --config "${SCRIPT_DIR}/kind-config.yaml"
        log_success "KinD cluster '${CLUSTER_NAME}' created."
    fi

    # 2. Install KubeRay Operator via Helm
    log_info "Installing / upgrading KubeRay operator via Helm..."
    helm repo add kuberay https://ray-project.github.io/kuberay-helm/ --force-update 2>/dev/null || helm repo add kuberay https://ray-project.github.io/kuberay-helm/
    helm repo update
    helm upgrade --install kuberay-operator kuberay/kuberay-operator --namespace "${NAMESPACE}" --create-namespace

    log_info "Waiting for KubeRay operator deployment to be Available..."
    kubectl wait --for=condition=Available deployment/kuberay-operator -n "${NAMESPACE}" --timeout=120s
    log_success "KubeRay operator is running."

    # 3. Apply RayCluster Manifest
    log_info "Applying RayCluster manifest ${SCRIPT_DIR}/ray-cluster.yaml..."
    kubectl apply -f "${SCRIPT_DIR}/ray-cluster.yaml"

    # 4. Wait for pods to become ready
    cluster_wait

    log_success "KubeRay cluster '${RAY_CLUSTER_NAME}' is fully up and ready!"
    echo -e "${BOLD}Next steps:${NC}"
    echo "  - Forward ports:  $0 forward"
    echo "  - Check status:   $0 status"
    echo "  - Teardown:       $0 down"
}

cluster_wait() {
    log_info "Waiting for Ray head pod to be Ready (timeout 180s)..."
    if ! kubectl wait --for=condition=Ready pod -l ray.io/node-type=head -n "${NAMESPACE}" --timeout=180s; then
        log_error "Ray head pod failed to reach Ready state."
        kubectl describe pods -l ray.io/node-type=head -n "${NAMESPACE}" || true
        exit 1
    fi

    log_info "Waiting for Ray worker pods to be Ready (timeout 180s)..."
    if ! kubectl wait --for=condition=Ready pod -l ray.io/node-type=worker -n "${NAMESPACE}" --timeout=180s; then
        log_error "Ray worker pods failed to reach Ready state."
        kubectl describe pods -l ray.io/node-type=worker -n "${NAMESPACE}" || true
        exit 1
    fi

    log_success "All Ray cluster pods are Ready."
}

cluster_forward() {
    log_info "Starting background port-forwarding for svc/${RAY_CLUSTER_NAME}-head-svc..."

    # Check if head service exists
    if ! kubectl get svc "${RAY_CLUSTER_NAME}-head-svc" -n "${NAMESPACE}" &>/dev/null; then
        log_error "Service '${RAY_CLUSTER_NAME}-head-svc' not found in namespace '${NAMESPACE}'."
        exit 1
    fi

    # Kill existing port-forward on port 10001 or 8265 if running
    pkill -f "kubectl port-forward svc/${RAY_CLUSTER_NAME}-head-svc" 2>/dev/null || true

    local LOG_FILE="/tmp/kuberay-port-forward.log"
    nohup kubectl port-forward "svc/${RAY_CLUSTER_NAME}-head-svc" 10001:10001 8265:8265 -n "${NAMESPACE}" > "${LOG_FILE}" 2>&1 &
    local PF_PID=$!
    disown "$PF_PID" 2>/dev/null || true

    sleep 2

    if kill -0 "$PF_PID" 2>/dev/null; then
        log_success "Port-forwarding established (PID: ${PF_PID})."
        echo -e "  - Ray Client:    ${BOLD}ray://localhost:10001${NC}"
        echo -e "  - Ray Dashboard: ${BOLD}http://localhost:8265${NC}"
        echo -e "  - Forward Logs:  ${LOG_FILE}"
    else
        log_error "Port-forwarding failed to start. Logs:"
        cat "${LOG_FILE}"
        exit 1
    fi
}

cluster_status() {
    echo -e "${BOLD}=== KinD Nodes ===${NC}"
    kubectl get nodes -o wide || true
    echo ""

    echo -e "${BOLD}=== RayCluster CRD Status ===${NC}"
    kubectl get rayclusters -n "${NAMESPACE}" || true
    echo ""

    echo -e "${BOLD}=== Ray Pods ===${NC}"
    kubectl get pods -l ray.io/node-type -n "${NAMESPACE}" -o wide || true
    echo ""

    echo -e "${BOLD}=== Ray Head Services ===${NC}"
    kubectl get svc -l ray.io/node-type=head -n "${NAMESPACE}" || true
}

cluster_down() {
    log_info "Stopping background port-forwarding (if any)..."
    pkill -f "kubectl port-forward svc/${RAY_CLUSTER_NAME}-head-svc" 2>/dev/null || true

    log_info "Deleting KinD cluster '${CLUSTER_NAME}'..."
    kind delete cluster --name "${CLUSTER_NAME}"
    log_success "KinD cluster '${CLUSTER_NAME}' deleted successfully."
}

show_help() {
    echo -e "${BOLD}Usage:${NC} $0 <command>"
    echo ""
    echo "Commands:"
    echo "  up       Create KinD cluster, install KubeRay operator, deploy RayCluster, and wait for readiness"
    echo "  down     Delete KinD cluster and clean up resources"
    echo "  wait     Wait for Ray head and worker pods to reach Ready state"
    echo "  forward  Port-forward Ray Client (10001) and Dashboard (8265) to localhost in background"
    echo "  status   Display status of KinD nodes, RayCluster resource, and Ray pods"
    echo "  help     Show this help message"
}

case "${1:-help}" in
    up)
        cluster_up
        ;;
    down)
        cluster_down
        ;;
    wait)
        cluster_wait
        ;;
    forward)
        cluster_forward
        ;;
    status)
        cluster_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
