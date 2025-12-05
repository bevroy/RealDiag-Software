# Deploy Changes to www.realdiag.com

## 🚨 Current Issue

Changes pushed to GitHub are not appearing on www.realdiag.com because:
- Kubernetes deployment uses **fixed image tags** (`v1.4.0`)
- Recent code changes are built with `:latest` tag but not deployed

## ✅ Solution Applied

Updated `k8s/production-realdiag.yaml` to use `:latest` tags:
- Backend: `ghcr.io/bevroy/realdiag-backend:latest`
- Frontend: `ghcr.io/bevroy/realdiag-frontend:latest`

## 🚀 Deploy to Production

### Step 1: Wait for GitHub Actions

GitHub Actions automatically builds and pushes new Docker images:

```bash
# Check build status
gh run list --limit 3
```

Wait for **"Build & Publish Images"** workflow to complete ✅

### Step 2: Deploy to Kubernetes

Connect to your production cluster and run:

```bash
# Restart backend API deployment (pulls latest image)
kubectl rollout restart deployment/realdiag-api -n production

# Restart frontend web deployment (pulls latest image)
kubectl rollout restart deployment/realdiag-web -n production
```

### Step 3: Verify Deployment

```bash
# Check rollout status
kubectl rollout status deployment/realdiag-api -n production
kubectl rollout status deployment/realdiag-web -n production

# Verify pods are running
kubectl get pods -n production

# Check logs
kubectl logs -l app=realdiag-api -n production --tail=50
```

### Step 4: Test on www.realdiag.com

```bash
# Test API health
curl https://api.realdiag.com/health

# Check version (should show new features)
curl https://api.realdiag.com/diagnostic/trees
```

## 📋 Quick Deploy Script

Save this as `deploy-latest.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying latest changes to www.realdiag.com..."

# Wait for GitHub Actions to complete
echo "⏳ Checking GitHub Actions status..."
gh run list --limit 1 --json status,conclusion --jq '.[0] | .status + " " + .conclusion'

# Deploy to Kubernetes
echo "🔄 Restarting deployments..."
kubectl rollout restart deployment/realdiag-api -n production
kubectl rollout restart deployment/realdiag-web -n production

# Wait for rollout
echo "⏳ Waiting for deployments to complete..."
kubectl rollout status deployment/realdiag-api -n production
kubectl rollout status deployment/realdiag-web -n production

# Verify
echo "✅ Testing endpoints..."
curl -f https://api.realdiag.com/health || echo "❌ API health check failed"

echo "✅ Deployment complete!"
echo "🌐 Visit www.realdiag.com to see changes"
```

Then run:
```bash
chmod +x deploy-latest.sh
./deploy-latest.sh
```

## 🔧 Alternative: Manual Image Tag Update

If you prefer to control which version deploys, use commit SHA tags:

```bash
# Get current commit SHA
COMMIT_SHA=$(git rev-parse --short HEAD)

# Update deployment with specific commit
kubectl set image deployment/realdiag-api \
  realdiag-api=ghcr.io/bevroy/realdiag-backend:$COMMIT_SHA \
  -n production

kubectl set image deployment/realdiag-web \
  realdiag-web=ghcr.io/bevroy/realdiag-frontend:$COMMIT_SHA \
  -n production
```

## 📊 Recent Changes to Deploy

**Commit `11f20ad` - EMR Medication Integration**
- Automatic medication pull from FHIR EMR
- Real-time medication safety checking
- New endpoint: `/diagnostic/emr/patient/{id}/medications`

**Commit `99e23fe` - Medication Safety Service**
- Drug-drug interaction checking (25+ interactions)
- Contraindication alerts (15+ medication-condition pairs)
- Allergen cross-reactivity warnings (10+ patterns)
- Safety score calculation (0-100)

## 🔍 Troubleshooting

### Images not updating?

```bash
# Force pull latest images
kubectl delete pod -l app=realdiag-api -n production
kubectl delete pod -l app=realdiag-web -n production
```

### Check image versions running:

```bash
kubectl get pods -n production -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'
```

### View deployment history:

```bash
kubectl rollout history deployment/realdiag-api -n production
kubectl rollout history deployment/realdiag-web -n production
```

### Rollback if needed:

```bash
kubectl rollout undo deployment/realdiag-api -n production
kubectl rollout undo deployment/realdiag-web -n production
```

## 🔒 Access Requirements

You need:
- ✅ `kubectl` access to production cluster
- ✅ Namespace permissions for `production`
- ✅ GitHub Actions completed successfully
- ✅ Docker images pushed to `ghcr.io/bevroy/`

## 📝 Future: Automated CD

To avoid manual deployments, set up automatic CD:

```yaml
# .github/workflows/cd-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl rollout restart deployment/realdiag-api -n production
          kubectl rollout restart deployment/realdiag-web -n production
```

This would automatically deploy every push to main! 🚀

---

**Current Status:** ✅ Fixed - deployment configuration updated to use `:latest` tags  
**Action Required:** Run Step 2 above to deploy changes to www.realdiag.com
