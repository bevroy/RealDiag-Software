#!/bin/bash
# RealDiag Kubernetes Deployment Script
# Usage: ./deploy.sh [environment] [action]
# Example: ./deploy.sh production deploy
#          ./deploy.sh production rollback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}
NAMESPACE="$ENVIRONMENT"
K8S_DIR="$(dirname "$0")"
VERSION=$(cat VERSION 2>/dev/null || echo "v1.4.0")

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}RealDiag Kubernetes Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Environment: $ENVIRONMENT"
echo "Action: $ACTION"
echo "Version: $VERSION"
echo "Namespace: $NAMESPACE"
echo ""

# Functions
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl not found${NC}"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}Error: helm not found${NC}"
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
    echo ""
}

create_namespace() {
    echo -e "${YELLOW}Creating namespace: $NAMESPACE${NC}"
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace $NAMESPACE environment=$ENVIRONMENT --overwrite
    
    echo -e "${GREEN}✓ Namespace ready${NC}"
    echo ""
}

deploy_secrets() {
    echo -e "${YELLOW}Deploying secrets...${NC}"
    
    # Check if secrets file exists
    if [ ! -f "$K8S_DIR/configmap.yaml" ]; then
        echo -e "${RED}Error: configmap.yaml not found${NC}"
        exit 1
    fi
    
    # Warning about secret values
    echo -e "${YELLOW}⚠️  WARNING: Update secret values before deploying to production!${NC}"
    read -p "Have you updated the secret values? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
    
    kubectl apply -f "$K8S_DIR/configmap.yaml" -n $NAMESPACE
    
    echo -e "${GREEN}✓ Secrets and ConfigMaps deployed${NC}"
    echo ""
}

deploy_statefulsets() {
    echo -e "${YELLOW}Deploying StatefulSets (Database & Cache)...${NC}"
    
    kubectl apply -f "$K8S_DIR/statefulsets.yaml" -n $NAMESPACE
    
    # Wait for StatefulSets to be ready
    echo "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgresql -n $NAMESPACE --timeout=300s
    
    echo "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    
    echo -e "${GREEN}✓ StatefulSets deployed and ready${NC}"
    echo ""
}

deploy_backend() {
    echo -e "${YELLOW}Deploying backend API...${NC}"
    
    kubectl apply -f "$K8S_DIR/backend-deployment.yaml" -n $NAMESPACE
    
    # Wait for deployment to be ready
    echo "Waiting for backend pods to be ready..."
    kubectl wait --for=condition=available deployment/realdiag-api -n $NAMESPACE --timeout=300s
    
    echo -e "${GREEN}✓ Backend deployed${NC}"
    echo ""
}

deploy_frontend() {
    echo -e "${YELLOW}Deploying frontend web...${NC}"
    
    kubectl apply -f "$K8S_DIR/frontend-deployment.yaml" -n $NAMESPACE
    
    # Wait for deployment to be ready
    echo "Waiting for frontend pods to be ready..."
    kubectl wait --for=condition=available deployment/realdiag-web -n $NAMESPACE --timeout=300s
    
    echo -e "${GREEN}✓ Frontend deployed${NC}"
    echo ""
}

deploy_hpa() {
    echo -e "${YELLOW}Deploying Horizontal Pod Autoscalers...${NC}"
    
    kubectl apply -f "$K8S_DIR/hpa.yaml" -n $NAMESPACE
    
    echo -e "${GREEN}✓ HPA deployed${NC}"
    echo ""
}

deploy_ingress() {
    echo -e "${YELLOW}Deploying Ingress...${NC}"
    
    # Check if cert-manager is installed
    if ! kubectl get crd certificates.cert-manager.io &> /dev/null; then
        echo -e "${YELLOW}⚠️  cert-manager not found. Installing...${NC}"
        kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
        echo "Waiting for cert-manager to be ready..."
        sleep 30
    fi
    
    kubectl apply -f "$K8S_DIR/ingress.yaml" -n $NAMESPACE
    
    echo -e "${GREEN}✓ Ingress deployed${NC}"
    echo ""
}

deploy_monitoring() {
    echo -e "${YELLOW}Deploying monitoring (Prometheus + Grafana)...${NC}"
    
    # Check if monitoring namespace exists
    if ! kubectl get namespace monitoring &> /dev/null; then
        kubectl create namespace monitoring
    fi
    
    # Install Prometheus + Grafana using Helm
    if ! helm list -n monitoring | grep -q prometheus; then
        echo "Installing Prometheus stack..."
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
        helm install prometheus prometheus-community/kube-prometheus-stack \
            --namespace monitoring \
            --set grafana.adminPassword='RealDiag2024!' \
            --wait
    fi
    
    # Apply alert rules
    kubectl apply -f "$K8S_DIR/prometheus-rules.yaml" -n monitoring
    
    echo -e "${GREEN}✓ Monitoring deployed${NC}"
    echo ""
}

show_status() {
    echo -e "${YELLOW}Deployment Status:${NC}"
    echo ""
    
    echo "Pods:"
    kubectl get pods -n $NAMESPACE
    echo ""
    
    echo "Services:"
    kubectl get svc -n $NAMESPACE
    echo ""
    
    echo "Ingress:"
    kubectl get ingress -n $NAMESPACE
    echo ""
    
    echo "HPA:"
    kubectl get hpa -n $NAMESPACE
    echo ""
}

rollback() {
    echo -e "${YELLOW}Rolling back deployment...${NC}"
    
    # Rollback backend
    echo "Rolling back backend..."
    kubectl rollout undo deployment/realdiag-api -n $NAMESPACE
    kubectl rollout status deployment/realdiag-api -n $NAMESPACE
    
    # Rollback frontend
    echo "Rolling back frontend..."
    kubectl rollout undo deployment/realdiag-web -n $NAMESPACE
    kubectl rollout status deployment/realdiag-web -n $NAMESPACE
    
    echo -e "${GREEN}✓ Rollback completed${NC}"
    echo ""
}

verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"
    
    # Check pod health
    UNHEALTHY_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
    if [ "$UNHEALTHY_PODS" -gt 0 ]; then
        echo -e "${RED}Warning: $UNHEALTHY_PODS unhealthy pods found${NC}"
        kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running
    else
        echo -e "${GREEN}✓ All pods are healthy${NC}"
    fi
    
    # Check service endpoints
    echo ""
    echo "Service endpoints:"
    kubectl get endpoints -n $NAMESPACE
    
    echo ""
    echo -e "${GREEN}Deployment verification complete${NC}"
    echo ""
}

get_access_info() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Access Information${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Get Ingress IP
    INGRESS_IP=$(kubectl get ingress realdiag-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending...")
    echo "Ingress IP: $INGRESS_IP"
    echo ""
    
    echo "Application URLs:"
    echo "  API: https://api.realdiag.com"
    echo "  Web: https://app.realdiag.com"
    echo ""
    
    echo "Grafana Dashboard:"
    echo "  kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
    echo "  Then visit: http://localhost:3000"
    echo "  Username: admin"
    echo "  Password: RealDiag2024!"
    echo ""
    
    echo "Prometheus:"
    echo "  kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
    echo "  Then visit: http://localhost:9090"
    echo ""
}

cleanup() {
    echo -e "${YELLOW}Cleaning up resources...${NC}"
    
    read -p "Are you sure you want to delete all resources in namespace $NAMESPACE? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleanup cancelled"
        exit 0
    fi
    
    kubectl delete namespace $NAMESPACE
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Main deployment flow
case $ACTION in
    deploy)
        check_prerequisites
        create_namespace
        deploy_secrets
        deploy_statefulsets
        deploy_backend
        deploy_frontend
        deploy_hpa
        deploy_ingress
        deploy_monitoring
        verify_deployment
        show_status
        get_access_info
        ;;
    
    rollback)
        rollback
        show_status
        ;;
    
    status)
        show_status
        ;;
    
    verify)
        verify_deployment
        ;;
    
    info)
        get_access_info
        ;;
    
    cleanup)
        cleanup
        ;;
    
    *)
        echo "Usage: $0 [environment] [action]"
        echo ""
        echo "Actions:"
        echo "  deploy    - Full deployment (default)"
        echo "  rollback  - Rollback to previous version"
        echo "  status    - Show deployment status"
        echo "  verify    - Verify deployment health"
        echo "  info      - Show access information"
        echo "  cleanup   - Delete all resources"
        echo ""
        echo "Examples:"
        echo "  $0 production deploy"
        echo "  $0 production rollback"
        echo "  $0 staging status"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
