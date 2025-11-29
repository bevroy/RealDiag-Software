# Production Deployment Guide

## Overview

This guide covers deploying RealDiag to a production Kubernetes cluster with high availability, security, and monitoring.

## Prerequisites

- Kubernetes cluster (v1.24+)
- `kubectl` configured with cluster access
- `cert-manager` installed for TLS certificates
- NGINX Ingress Controller installed
- PostgreSQL and Redis databases (can be external or in-cluster)
- Domain names configured:
  - `realdiag.com` (web)
  - `api.realdiag.com` (API)
- Container images pushed to GHCR:
  - `ghcr.io/bevroy/realdiag-api:v1.4.0`
  - `ghcr.io/bevroy/realdiag-web:v1.4.0`

## Architecture

### High Availability
- **3 replicas** minimum for API and Web
- **HorizontalPodAutoscaler**: 3-10 replicas based on CPU/memory
- **PodDisruptionBudget**: Ensures 2 pods always available during updates
- **Pod Anti-Affinity**: Distributes pods across nodes

### Security
- **Non-root containers**: All pods run as user 1000
- **Read-only filesystem**: Prevents container modifications
- **Dropped capabilities**: Minimal Linux capabilities
- **Network policies**: Restricts traffic to required services only
- **TLS termination**: cert-manager with Let's Encrypt
- **Secrets management**: Kubernetes secrets (recommend External Secrets Operator)

### Performance
- **Resource limits**: 250m-1Gi CPU, 256Mi-1Gi memory
- **Health probes**: Startup, readiness, and liveness checks
- **Zero-downtime deployments**: Rolling updates with maxUnavailable=0
- **Session affinity**: Sticky sessions for API

### Monitoring
- **Prometheus metrics**: ServiceMonitor for scraping
- **Sentry error tracking**: Both frontend and backend
- **Structured logging**: JSON format with correlation IDs

## Pre-Deployment Checklist

### 1. Build and Push Container Images

```bash
# Backend
cd backend
docker build -t ghcr.io/bevroy/realdiag-api:v1.4.0 .
docker push ghcr.io/bevroy/realdiag-api:v1.4.0

# Frontend
cd ../frontend
docker build -t ghcr.io/bevroy/realdiag-web:v1.4.0 .
docker push ghcr.io/bevroy/realdiag-web:v1.4.0
```

### 2. Create GitHub Container Registry Pull Secret

```bash
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=bevroy \
  --docker-password=$GITHUB_TOKEN \
  --namespace=production
```

### 3. Generate Production Secrets

```bash
# Generate secure random secrets
export JWT_SECRET=$(openssl rand -base64 32)
export DB_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)

# Get Sentry DSN from https://sentry.io
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"

# Create secrets file (DO NOT COMMIT!)
cat > .env.production.secrets <<EOF
JWT_SECRET_KEY=$JWT_SECRET
DATABASE_PASSWORD=$DB_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
SENTRY_DSN=$SENTRY_DSN
EOF

# Create Kubernetes secret
kubectl create secret generic realdiag-secrets \
  --from-env-file=.env.production.secrets \
  --namespace=production

# Securely delete secrets file
shred -u .env.production.secrets
unset JWT_SECRET DB_PASSWORD REDIS_PASSWORD SENTRY_DSN
```

### 4. Configure DNS

Point your domains to the Ingress Controller's LoadBalancer IP:

```bash
# Get LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Create A records
realdiag.com          -> [LoadBalancer-IP]
www.realdiag.com      -> [LoadBalancer-IP]
api.realdiag.com      -> [LoadBalancer-IP]
```

### 5. Install cert-manager (if not already installed)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create Let's Encrypt ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@realdiag.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Deployment Steps

### 1. Review Configuration

```bash
# Review the production configuration
cat k8s/production-realdiag.yaml

# Check for required changes:
# - Update image versions if needed
# - Verify domain names
# - Adjust resource limits based on load testing
# - Review replica counts and autoscaling limits
```

### 2. Dry-Run Deployment

```bash
# Validate configuration
kubectl apply -f k8s/production-realdiag.yaml --dry-run=client

# Validate against cluster
kubectl apply -f k8s/production-realdiag.yaml --dry-run=server
```

### 3. Deploy to Production

```bash
# Deploy all resources
kubectl apply -f k8s/production-realdiag.yaml

# Watch rollout
kubectl rollout status deployment/realdiag-api -n production
kubectl rollout status deployment/realdiag-web -n production
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n production

# Check pods are running
kubectl get pods -n production
# Should show:
# - 3 realdiag-api pods
# - 3 realdiag-web pods
# - All STATUS: Running

# Check services
kubectl get svc -n production

# Check ingress
kubectl get ingress -n production

# Check HPA
kubectl get hpa -n production

# Check certificates
kubectl get certificate -n production
# Should show: READY=True for realdiag-tls
```

### 5. Test Application

```bash
# Test API health
curl https://api.realdiag.com/health/readiness
# Should return: {"status": "healthy"}

# Test web frontend
curl -I https://realdiag.com
# Should return: 200 OK

# Test TLS certificate
openssl s_client -connect realdiag.com:443 -servername realdiag.com < /dev/null
# Should show valid Let's Encrypt certificate
```

### 6. Monitor Logs

```bash
# API logs
kubectl logs -n production deployment/realdiag-api --tail=100 -f

# Web logs
kubectl logs -n production deployment/realdiag-web --tail=100 -f

# Check for errors
kubectl logs -n production deployment/realdiag-api | grep -i error
kubectl logs -n production deployment/realdiag-web | grep -i error

# Check Sentry initialization
kubectl logs -n production deployment/realdiag-api | grep -i sentry
# Should see: "Sentry initialized for environment: production"
```

### 7. Performance Testing

```bash
# Basic load test
ab -n 1000 -c 10 https://api.realdiag.com/health/readiness

# Or use hey
hey -n 1000 -c 10 https://api.realdiag.com/health/readiness

# Monitor HPA during load
watch kubectl get hpa -n production
# Should see replicas increase if load is sufficient
```

## Post-Deployment Configuration

### 1. Set Up Monitoring

```bash
# Verify Prometheus scraping (if using Prometheus Operator)
kubectl get servicemonitor -n production

# Check metrics endpoint
kubectl port-forward -n production svc/realdiag-api 9090:9090
curl http://localhost:9090/metrics
```

### 2. Configure Alerts

Create alerts in Sentry (see `docs/SENTRY_SETUP.md`):
- High error rate
- Critical errors
- Performance degradation
- User impact

### 3. Set Up Backups

```bash
# Database backups (example for PostgreSQL)
kubectl create cronjob postgres-backup \
  --image=postgres:15 \
  --schedule="0 2 * * *" \
  --namespace=production \
  -- pg_dump -h postgresql-service -U postgres -d realdiag > /backups/realdiag-$(date +%Y%m%d).sql
```

### 4. Configure Log Aggregation

Set up log shipping to your preferred solution:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki + Grafana
- Cloud provider logging (CloudWatch, Cloud Logging, Azure Monitor)

Example Fluent Bit DaemonSet for log collection:

```yaml
# fluent-bit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: production
data:
  fluent-bit.conf: |
    [INPUT]
        Name              tail
        Path              /var/log/containers/*production*.log
        Parser            docker
        Tag               kube.*
        Mem_Buf_Limit     5MB
    
    [OUTPUT]
        Name  es
        Match *
        Host  elasticsearch.logging.svc.cluster.local
        Port  9200
        Index realdiag
```

## Updating the Application

### Rolling Update

```bash
# Update image versions in k8s/production-realdiag.yaml
# Then apply changes
kubectl apply -f k8s/production-realdiag.yaml

# Monitor rollout
kubectl rollout status deployment/realdiag-api -n production
kubectl rollout status deployment/realdiag-web -n production

# Check rollout history
kubectl rollout history deployment/realdiag-api -n production
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/realdiag-api -n production
kubectl rollout undo deployment/realdiag-web -n production

# Or rollback to specific revision
kubectl rollout undo deployment/realdiag-api -n production --to-revision=2
```

### Blue-Green Deployment

For zero-downtime updates with instant rollback:

```bash
# Create new deployment with different label
kubectl apply -f k8s/production-realdiag-blue.yaml

# Wait for new pods to be ready
kubectl wait --for=condition=ready pod -l app=realdiag-api,version=blue -n production

# Switch service selector
kubectl patch service realdiag-api -n production -p '{"spec":{"selector":{"version":"blue"}}}'

# Monitor for issues, rollback if needed
kubectl patch service realdiag-api -n production -p '{"spec":{"selector":{"version":"green"}}}'

# Clean up old deployment
kubectl delete deployment realdiag-api-green -n production
```

## Scaling

### Manual Scaling

```bash
# Scale deployments
kubectl scale deployment/realdiag-api --replicas=5 -n production
kubectl scale deployment/realdiag-web --replicas=5 -n production
```

### Autoscaling Configuration

Edit HPA in `k8s/production-realdiag.yaml`:

```yaml
spec:
  minReplicas: 3
  maxReplicas: 20  # Increase max replicas
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60  # Scale earlier (lower threshold)
```

### Cluster Autoscaling

Ensure cluster autoscaler is configured to add nodes when needed:

```yaml
# For AWS EKS
eksctl scale nodegroup --cluster=prod-cluster --name=ng-prod --nodes=5 --nodes-min=3 --nodes-max=10

# For GKE
gcloud container clusters update prod-cluster --enable-autoscaling --min-nodes=3 --max-nodes=10

# For AKS
az aks update --resource-group myResourceGroup --name prod-cluster --enable-cluster-autoscaler --min-count=3 --max-count=10
```

## Disaster Recovery

### Backup Strategy

1. **Database**: Daily automated backups with 30-day retention
2. **Secrets**: Store encrypted in secure vault (AWS Secrets Manager, Azure Key Vault)
3. **Configuration**: All YAML files in version control
4. **Container Images**: Tagged and stored in GHCR with immutable tags

### Recovery Procedure

```bash
# 1. Restore database from backup
kubectl exec -it postgresql-0 -n production -- psql -U postgres -d realdiag < backup.sql

# 2. Recreate secrets
kubectl create secret generic realdiag-secrets --from-env-file=.env.backup -n production

# 3. Redeploy application
kubectl apply -f k8s/production-realdiag.yaml

# 4. Verify health
kubectl get pods -n production
curl https://api.realdiag.com/health/readiness
```

### Disaster Recovery Testing

Schedule quarterly DR drills:
1. Simulate database failure
2. Test backup restoration
3. Measure recovery time objective (RTO)
4. Document lessons learned

## Security Best Practices

### 1. Regular Updates

```bash
# Update base images monthly
# Update dependencies weekly
# Apply security patches immediately

# Scan images for vulnerabilities
docker scan ghcr.io/bevroy/realdiag-api:v1.4.0
```

### 2. Secret Rotation

```bash
# Rotate JWT secret every 90 days
NEW_SECRET=$(openssl rand -base64 32)
kubectl create secret generic realdiag-secrets-new \
  --from-literal=JWT_SECRET_KEY=$NEW_SECRET \
  -n production

# Update deployment to use new secret
# Then delete old secret
kubectl delete secret realdiag-secrets -n production
kubectl rename secret realdiag-secrets-new realdiag-secrets -n production
```

### 3. Network Policies

The production config includes NetworkPolicy to restrict traffic. Verify:

```bash
kubectl get networkpolicy -n production
kubectl describe networkpolicy realdiag-network-policy -n production
```

### 4. RBAC

Create minimal service accounts:

```bash
kubectl create serviceaccount realdiag-api -n production
kubectl create role realdiag-api-role --verb=get,list --resource=configmaps,secrets -n production
kubectl create rolebinding realdiag-api-binding --role=realdiag-api-role --serviceaccount=production:realdiag-api -n production
```

### 5. Pod Security Standards

Enable Pod Security Admission:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Monitoring and Observability

### Key Metrics to Monitor

1. **Application Metrics**
   - Request rate (requests/sec)
   - Error rate (%)
   - Response time (p50, p95, p99)
   - Active users

2. **Infrastructure Metrics**
   - CPU utilization (%)
   - Memory utilization (%)
   - Disk I/O
   - Network throughput

3. **Business Metrics**
   - Diagnostic searches per hour
   - User registrations per day
   - API success rate
   - Average session duration

### Grafana Dashboard

Import pre-built dashboards:
- Kubernetes Cluster Monitoring (ID: 315)
- NGINX Ingress Controller (ID: 9614)
- FastAPI Metrics (custom - see `backend/metrics.py`)

### Alert Rules

```yaml
# prometheus-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: realdiag-alerts
  namespace: production
spec:
  groups:
  - name: realdiag
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: sum(rate(http_requests_total{status=~"5.."}[5m])) > 10
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
    
    - alert: HighResponseTime
      expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High response time (p95 > 2s)"
```

## Cost Optimization

### Right-Sizing Resources

After monitoring for a week, adjust resources:

```yaml
resources:
  requests:
    cpu: 200m  # Reduce if avg usage < 150m
    memory: 200Mi  # Reduce if avg usage < 150Mi
  limits:
    cpu: 800m  # Keep headroom for spikes
    memory: 800Mi
```

### Autoscaling Tuning

```yaml
# Be conservative with scale-down
behavior:
  scaleDown:
    stabilizationWindowSeconds: 600  # Wait 10 minutes
    policies:
      - type: Percent
        value: 25  # Scale down by 25% at most
        periodSeconds: 60
```

### Spot Instances (for non-critical workloads)

```yaml
# Node affinity for spot instances
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      preference:
        matchExpressions:
        - key: kubernetes.io/capacity-type
          operator: In
          values:
          - spot
```

## Compliance (HIPAA)

For HIPAA compliance:

1. **Encrypt data at rest**: Enable encryption for PVCs
2. **Encrypt data in transit**: TLS everywhere (configured in Ingress)
3. **Access controls**: RBAC, NetworkPolicies (configured)
4. **Audit logging**: Enable Kubernetes audit logs
5. **Sign BAA**: With cloud provider, Sentry, and other vendors
6. **Regular security assessments**: Quarterly penetration tests
7. **Incident response plan**: Document and test procedures

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod [pod-name] -n production

# Common issues:
# - ImagePullBackOff: Check image name and pull secret
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Check resource limits and node capacity
```

### High error rates

```bash
# Check pod logs
kubectl logs -n production deployment/realdiag-api --tail=1000 | grep ERROR

# Check Sentry dashboard for detailed errors
# Check database connectivity
kubectl exec -it [api-pod] -n production -- curl http://postgresql-service:5432
```

### Performance issues

```bash
# Check resource usage
kubectl top pods -n production

# Check if HPA is working
kubectl describe hpa realdiag-api-hpa -n production

# Check for throttling
kubectl describe pod [pod-name] -n production | grep -i throttl
```

### Certificate issues

```bash
# Check certificate status
kubectl describe certificate realdiag-tls -n production

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Manually trigger certificate renewal
kubectl delete secret realdiag-tls -n production
# cert-manager will automatically recreate it
```

## Support and Maintenance

### Regular Maintenance Tasks

- **Daily**: Monitor error rates, check Sentry dashboard
- **Weekly**: Review resource usage, update dependencies
- **Monthly**: Security patches, certificate expiry check, backup testing
- **Quarterly**: DR drill, penetration testing, cost review
- **Annually**: Architecture review, capacity planning

### On-Call Runbook

1. **High error rate alert**
   - Check Sentry for error details
   - Review recent deployments (rollback if needed)
   - Scale up if load-related
   - Check database/Redis connectivity

2. **High response time alert**
   - Check HPA status (scale up if needed)
   - Review slow queries in logs
   - Check external service latency
   - Consider rate limiting aggressive clients

3. **Pod crashes**
   - Review pod logs
   - Check resource limits
   - Look for OOM kills
   - Review recent code changes

4. **Certificate expiry**
   - Check cert-manager logs
   - Manually trigger renewal if needed
   - Verify DNS records for ACME challenge

## Next Steps

After successful deployment:

1. ✅ Application deployed and healthy
2. ⬜ Set up monitoring dashboards
3. ⬜ Configure alerting rules
4. ⬜ Implement log aggregation
5. ⬜ Schedule backup testing
6. ⬜ Conduct load testing
7. ⬜ Document incident response procedures
8. ⬜ Train team on operations
9. ⬜ Plan DR drill
10. ⬜ Get HIPAA audit if handling PHI

## References

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Production Best Practices](https://kubernetes.io/docs/setup/best-practices/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [Sentry Documentation](https://docs.sentry.io)
- [RealDiag Secrets Management](./SECRETS_MANAGEMENT.md)
- [RealDiag Sentry Setup](./SENTRY_SETUP.md)
