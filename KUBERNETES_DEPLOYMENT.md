# Kubernetes Deployment Guide - RealDiag

**Enterprise-Grade Infrastructure with High Availability**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Detailed Deployment](#detailed-deployment)
6. [Configuration](#configuration)
7. [Scaling](#scaling)
8. [Monitoring](#monitoring)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)
11. [Production Checklist](#production-checklist)

---

## Overview

This Kubernetes deployment provides:

- **High Availability**: 3+ replicas per service with pod anti-affinity
- **Auto-Scaling**: HPA based on CPU/memory metrics (3-10 replicas)
- **Zero-Downtime Deployments**: Rolling updates with health checks
- **Persistent Storage**: StatefulSets for PostgreSQL and Redis
- **SSL/TLS**: Automatic certificate management with Let's Encrypt
- **Network Security**: NetworkPolicies restricting traffic flow
- **Monitoring**: Prometheus + Grafana stack with custom metrics
- **Backup**: Automated daily PostgreSQL backups
- **Resource Management**: Requests/limits for all containers

---

## Architecture

```
                          Internet
                             |
                        [Ingress + SSL]
                             |
              +--------------+---------------+
              |                              |
         [Web Frontend]               [API Backend]
         (3-10 replicas)              (3-10 replicas)
              |                              |
              |                    +---------+----------+
              |                    |                    |
              |              [PostgreSQL]          [Redis]
              |              (StatefulSet)      (StatefulSet)
              |                    |                    |
              +--------------------+--------------------+
                             |
                    [Persistent Volumes]
```

### Component Summary

| Component | Type | Replicas | Storage | Purpose |
|-----------|------|----------|---------|---------|
| Backend API | Deployment | 3-10 | Ephemeral | FastAPI application |
| Frontend Web | Deployment | 3-10 | Ephemeral | Next.js application |
| PostgreSQL | StatefulSet | 1 | 20Gi | Primary database |
| Redis | StatefulSet | 1 | 5Gi | Cache & sessions |
| Prometheus | Deployment | 1 | 50Gi | Metrics collection |
| Grafana | Deployment | 1 | 10Gi | Visualization |

---

## Prerequisites

### Required Tools

```bash
# Kubernetes CLI
kubectl version --client  # v1.25+

# Helm package manager
helm version  # v3.10+

# Docker (for building images)
docker version  # 20.10+
```

### Cluster Requirements

- **Kubernetes**: v1.25+
- **Nodes**: 3+ worker nodes (recommended)
- **CPU**: 8+ cores total
- **Memory**: 16+ GB total
- **Storage**: 100+ GB available (for PVCs)
- **LoadBalancer**: Cloud provider LB or MetalLB for on-prem
- **StorageClass**: Default storage class configured

### Cloud Provider Support

This configuration works with:
- Google Kubernetes Engine (GKE)
- Amazon Elastic Kubernetes Service (EKS)
- Azure Kubernetes Service (AKS)
- DigitalOcean Kubernetes (DOKS)
- On-premise with MetalLB

---

## Quick Start

### 1. Build and Push Docker Images

```bash
# Backend
cd /workspaces/RealDiag-Software
docker build -t your-registry/realdiag-backend:v1.4.0 -f backend/Dockerfile .
docker push your-registry/realdiag-backend:v1.4.0

# Frontend
docker build -t your-registry/realdiag-frontend:v1.4.0 -f frontend/Dockerfile .
docker push your-registry/realdiag-frontend:v1.4.0
```

### 2. Update Configuration

```bash
cd k8s

# Update image references
sed -i 's|realdiag/backend:v1.4.0|your-registry/realdiag-backend:v1.4.0|g' backend-deployment.yaml
sed -i 's|realdiag/frontend:v1.4.0|your-registry/realdiag-frontend:v1.4.0|g' frontend-deployment.yaml

# Update secrets
vi configmap.yaml  # Update all CHANGE_ME values
```

### 3. Deploy

```bash
# Option A: Automated deployment script
./deploy.sh production deploy

# Option B: Manual deployment
kubectl create namespace production
kubectl apply -f configmap.yaml -n production
kubectl apply -f statefulsets.yaml -n production
kubectl apply -f backend-deployment.yaml -n production
kubectl apply -f frontend-deployment.yaml -n production
kubectl apply -f hpa.yaml -n production
kubectl apply -f ingress.yaml -n production
```

### 4. Verify Deployment

```bash
# Check status
./deploy.sh production status

# Or manually
kubectl get pods -n production
kubectl get svc -n production
kubectl get ingress -n production
```

---

## Detailed Deployment

### Step 1: Prepare Cluster

```bash
# Connect to your cluster
kubectl cluster-info

# Create namespace
kubectl create namespace production
kubectl label namespace production environment=production

# Set as default namespace (optional)
kubectl config set-context --current --namespace=production
```

### Step 2: Configure Secrets

**CRITICAL: Update all secret values before deploying!**

```bash
# Generate secure passwords
openssl rand -base64 32  # For DATABASE_URL password
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 32  # For JWT_SECRET
openssl rand -base64 32  # For REDIS_PASSWORD

# Edit configmap.yaml
vi k8s/configmap.yaml

# Update these values:
# - DATABASE_URL password
# - SENTRY_DSN (from Sentry.io)
# - SECRET_KEY
# - API_KEY
# - JWT_SECRET
# - REDIS_PASSWORD
# - POSTGRES_PASSWORD
# - Email address in ingress.yaml (for Let's Encrypt)
```

### Step 3: Deploy Database Layer

```bash
# Deploy PostgreSQL and Redis
kubectl apply -f k8s/statefulsets.yaml -n production

# Wait for StatefulSets to be ready
kubectl wait --for=condition=ready pod -l app=postgresql -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n production --timeout=300s

# Verify
kubectl get statefulsets -n production
kubectl get pvc -n production
```

### Step 4: Deploy Application Layer

```bash
# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml -n production

# Wait for backend to be ready
kubectl wait --for=condition=available deployment/realdiag-api -n production --timeout=300s

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml -n production

# Wait for frontend to be ready
kubectl wait --for=condition=available deployment/realdiag-web -n production --timeout=300s

# Verify
kubectl get deployments -n production
kubectl get pods -n production
```

### Step 5: Enable Auto-Scaling

```bash
# Deploy HPA
kubectl apply -f k8s/hpa.yaml -n production

# Verify HPA is working
kubectl get hpa -n production

# Check metrics (requires metrics-server)
kubectl top pods -n production
```

### Step 6: Configure Ingress & SSL

```bash
# Install cert-manager (if not already installed)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=available deployment -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Deploy ingress with Let's Encrypt
kubectl apply -f k8s/ingress.yaml -n production

# Check certificate status
kubectl get certificate -n production
kubectl describe certificate realdiag-tls-cert -n production

# Get external IP
kubectl get ingress -n production
```

### Step 7: Deploy Monitoring

```bash
# Install Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword='YourSecurePassword' \
  --wait

# Apply custom alert rules
kubectl apply -f k8s/prometheus-rules.yaml -n monitoring

# Port forward to access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Visit http://localhost:3000
# Username: admin
# Password: YourSecurePassword
```

---

## Configuration

### Environment Variables

All configuration is managed via ConfigMaps and Secrets:

**ConfigMap (Non-sensitive):**
- `ENVIRONMENT`: production/staging/development
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR
- `CORS_ORIGINS`: Allowed origins
- `PUBLIC_API_URL`: Public-facing API URL

**Secrets (Sensitive):**
- `DATABASE_URL`: PostgreSQL connection string
- `SENTRY_DSN`: Sentry error tracking DSN
- `SECRET_KEY`: Application secret key
- `API_KEY`: API authentication key
- `JWT_SECRET`: JWT signing key
- `REDIS_PASSWORD`: Redis authentication

### Resource Limits

**Backend API:**
```yaml
requests:
  cpu: 500m
  memory: 512Mi
limits:
  cpu: 2000m
  memory: 2Gi
```

**Frontend Web:**
```yaml
requests:
  cpu: 200m
  memory: 256Mi
limits:
  cpu: 1000m
  memory: 1Gi
```

**PostgreSQL:**
```yaml
requests:
  cpu: 500m
  memory: 1Gi
limits:
  cpu: 2000m
  memory: 4Gi
```

### Persistent Volumes

| Component | Size | Access Mode | Purpose |
|-----------|------|-------------|---------|
| PostgreSQL Data | 20Gi | ReadWriteOnce | Database files |
| Redis Data | 5Gi | ReadWriteOnce | Cache persistence |
| PostgreSQL Backups | 50Gi | ReadWriteOnce | Backup storage |
| Prometheus Data | 50Gi | ReadWriteOnce | Metrics storage |
| Grafana Data | 10Gi | ReadWriteOnce | Dashboard storage |

---

## Scaling

### Horizontal Pod Autoscaling

**Backend API:**
- Min Replicas: 3
- Max Replicas: 10
- Scale up: When CPU > 70% or Memory > 80%
- Scale down: After 5 minutes of low usage

**Frontend Web:**
- Min Replicas: 3
- Max Replicas: 10
- Scale up: When CPU > 70% or Memory > 80%
- Scale down: After 5 minutes of low usage

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment realdiag-api --replicas=5 -n production

# Scale frontend
kubectl scale deployment realdiag-web --replicas=5 -n production

# Check current replicas
kubectl get hpa -n production
```

### Vertical Pod Autoscaling (Optional)

```bash
# Install VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.13.0/vpa-v0.13.0.yaml

# Create VPA for backend
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: realdiag-api-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: realdiag-api
  updatePolicy:
    updateMode: "Auto"
EOF
```

---

## Monitoring

### Access Grafana Dashboard

```bash
# Port forward
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Visit http://localhost:3000
# Username: admin
# Password: (from Helm install)
```

### Import Custom Dashboard

```bash
# Import k8s/grafana-dashboard.json via Grafana UI
# Or use API:
curl -X POST http://admin:password@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @k8s/grafana-dashboard.json
```

### Key Metrics to Monitor

1. **Request Rate**: Track RPS per service
2. **Error Rate**: Monitor 4xx/5xx responses
3. **Latency**: P50/P95/P99 response times
4. **Saturation**: CPU/Memory usage
5. **Pod Health**: Restarts, readiness, liveness
6. **Database**: Connection pool, query time
7. **Cache**: Hit rate, memory usage

### Alerts

All alerts are defined in `k8s/prometheus-rules.yaml`:

- HighErrorRate (>5% for 5min)
- HighResponseTime (P95 >1s for 5min)
- HighCPUUsage (>80% for 5min)
- HighMemoryUsage (>80% for 5min)
- PodRestartLoop (>3 restarts in 10min)
- CertificateExpiringSoon (<7 days)

---

## Backup & Recovery

### Automated Backups

A CronJob runs daily at 2 AM to backup PostgreSQL:

```bash
# Check backup status
kubectl get cronjob postgresql-backup -n production
kubectl get jobs -n production | grep backup

# View backup logs
kubectl logs -l app=postgresql-backup -n production
```

### Manual Backup

```bash
# Backup database
kubectl exec -n production postgresql-0 -- \
  pg_dump -U realdiag_user realdiag | \
  gzip > backup-$(date +%Y%m%d).sql.gz

# Backup to cloud storage (example with AWS S3)
kubectl exec -n production postgresql-0 -- \
  pg_dump -U realdiag_user realdiag | \
  gzip | \
  aws s3 cp - s3://your-bucket/backups/realdiag-$(date +%Y%m%d).sql.gz
```

### Restore from Backup

```bash
# From local file
gunzip < backup-20241121.sql.gz | \
  kubectl exec -i -n production postgresql-0 -- \
  psql -U realdiag_user realdiag

# From S3
aws s3 cp s3://your-bucket/backups/realdiag-20241121.sql.gz - | \
  gunzip | \
  kubectl exec -i -n production postgresql-0 -- \
  psql -U realdiag_user realdiag
```

### Disaster Recovery

```bash
# 1. Deploy infrastructure
./deploy.sh production deploy

# 2. Restore database
kubectl exec -i -n production postgresql-0 -- \
  psql -U realdiag_user realdiag < backup.sql

# 3. Verify deployment
./deploy.sh production verify

# 4. Update DNS to point to new cluster
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -n production

# Describe pod for events
kubectl describe pod <pod-name> -n production

# Check logs
kubectl logs <pod-name> -n production

# Check previous logs (if crashed)
kubectl logs <pod-name> -n production --previous
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n production

# Test service from within cluster
kubectl run test --rm -it --image=busybox -n production -- sh
wget -O- http://realdiag-api:8000/health

# Check ingress
kubectl describe ingress realdiag-ingress -n production
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
kubectl logs -n production postgresql-0

# Test connection
kubectl exec -it -n production postgresql-0 -- \
  psql -U realdiag_user -d realdiag

# Check secret
kubectl get secret realdiag-secrets -n production -o yaml
```

### SSL Certificate Issues

```bash
# Check certificate status
kubectl get certificate -n production
kubectl describe certificate realdiag-tls-cert -n production

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Force renewal
kubectl delete certificate realdiag-tls-cert -n production
kubectl apply -f k8s/ingress.yaml -n production
```

### High Memory/CPU Usage

```bash
# Check resource usage
kubectl top pods -n production
kubectl top nodes

# Check HPA status
kubectl get hpa -n production
kubectl describe hpa realdiag-api-hpa -n production

# Check for memory leaks
kubectl exec -it <pod-name> -n production -- sh
ps aux
free -m
```

### Common Issues

| Issue | Solution |
|-------|----------|
| ImagePullBackOff | Check image name and registry credentials |
| CrashLoopBackOff | Check logs with `kubectl logs` |
| Pending Pods | Check node resources and PVC status |
| 503 Service Unavailable | Check if pods are ready, review health checks |
| Certificate Pending | Check cert-manager logs and DNS configuration |

---

## Production Checklist

### Pre-Deployment

- [ ] Update all secret values in `configmap.yaml`
- [ ] Generate secure passwords for all services
- [ ] Configure Sentry DSN
- [ ] Build and push Docker images to registry
- [ ] Update image references in deployment files
- [ ] Configure DNS records pointing to cluster
- [ ] Update email in `ingress.yaml` for Let's Encrypt
- [ ] Review and adjust resource limits
- [ ] Configure backup storage location
- [ ] Set up monitoring alert channels

### Post-Deployment

- [ ] Verify all pods are running: `kubectl get pods -n production`
- [ ] Check service endpoints: `kubectl get endpoints -n production`
- [ ] Test health endpoints: `curl https://api.realdiag.com/health`
- [ ] Verify SSL certificates: `kubectl get certificate -n production`
- [ ] Check ingress status: `kubectl get ingress -n production`
- [ ] Import Grafana dashboard
- [ ] Test alert firing
- [ ] Run load tests against production
- [ ] Verify backup job runs successfully
- [ ] Test database restore procedure
- [ ] Document rollback procedure
- [ ] Update runbooks with cluster-specific details
- [ ] Train team on kubectl commands

### Ongoing Operations

**Daily:**
- [ ] Check Grafana dashboard for anomalies
- [ ] Review Sentry errors
- [ ] Verify backup job completion

**Weekly:**
- [ ] Review HPA scaling events
- [ ] Check resource utilization trends
- [ ] Update Kubernetes version if needed
- [ ] Review and optimize resource requests/limits

**Monthly:**
- [ ] Test disaster recovery procedure
- [ ] Review and update alert thresholds
- [ ] Audit security policies
- [ ] Update dependencies and base images

---

## Quick Reference Commands

```bash
# Deployment
./deploy.sh production deploy
./deploy.sh production rollback
./deploy.sh production status

# Logs
kubectl logs -f -l app=realdiag-api -n production
kubectl logs -f -l app=realdiag-web -n production

# Shell access
kubectl exec -it <pod-name> -n production -- sh

# Port forwarding
kubectl port-forward -n production svc/realdiag-api 8000:8000
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Scaling
kubectl scale deployment realdiag-api --replicas=5 -n production

# Config updates
kubectl edit configmap realdiag-config -n production
kubectl rollout restart deployment/realdiag-api -n production

# Debug
kubectl describe pod <pod-name> -n production
kubectl get events -n production --sort-by=.metadata.creationTimestamp

# Cleanup
kubectl delete namespace production
```

---

## Support & Resources

- **Documentation**: See `/docs` folder for additional guides
- **Monitoring Guide**: `MONITORING_COMPLETION_REPORT.md`
- **Testing Guide**: `docs/TESTING_GUIDE.md`
- **Sentry Setup**: `docs/SENTRY_SETUP.md`
- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Helm Charts**: https://helm.sh/docs/

---

**Deployment Version:** v1.4.0  
**Last Updated:** November 21, 2025  
**Kubernetes Version:** 1.25+  
**Production Ready:** ✅ YES
