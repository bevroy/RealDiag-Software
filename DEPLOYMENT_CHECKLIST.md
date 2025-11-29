# Production Deployment Checklist ✓

**Date Started:** _______________  
**Deployed By:** _______________  
**Expected Completion:** 1-2 hours

---

## Pre-Deployment Preparation

- [ ] Review `MONITORING_COMPLETION_REPORT.md`
- [ ] Review `MONITORING_QUICK_START.md`
- [ ] Have access to:
  - [ ] Sentry.io account (or create one)
  - [ ] Kubernetes cluster (production)
  - [ ] Email/Slack/PagerDuty credentials for alerts
  - [ ] Production environment variables

---

## Step 1: Enable Sentry Error Tracking (5 minutes)

### 1.1 Get Sentry DSN
- [ ] Visit https://sentry.io
- [ ] Create account (if needed)
- [ ] Create new project: "realdiag-backend"
- [ ] Copy DSN from Settings > Projects > realdiag-backend > Client Keys (DSN)
- [ ] Create frontend project: "realdiag-frontend"
- [ ] Copy frontend DSN

**DSN (Backend):** `_________________________________`  
**DSN (Frontend):** `_________________________________`

### 1.2 Configure Environment
- [ ] Add to `.env` or Kubernetes secrets:
  ```bash
  SENTRY_DSN="https://your-key@sentry.io/project-id"
  ENVIRONMENT="production"
  SENTRY_TRACES_SAMPLE_RATE="0.1"
  SENTRY_PROFILES_SAMPLE_RATE="0.1"
  ```

### 1.3 Deploy and Verify
- [ ] Restart backend application
- [ ] Check logs for: `✅ Sentry initialized for environment: production`
- [ ] Test error capture: `curl http://localhost:8000/api/test-error`
- [ ] Verify error appears in Sentry dashboard
- [ ] Configure Sentry alerts (see `docs/SENTRY_SETUP.md`)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Step 2: Run Load Tests (15 minutes)

### 2.1 Baseline Test
- [ ] Ensure backend is running
- [ ] Run baseline test:
  ```bash
  locust -f tests/locustfile.py \
    --host=http://localhost:8000 \
    --users=50 --spawn-rate=5 \
    --run-time=5m --headless \
    --html=baseline_results.html
  ```
- [ ] Review `baseline_results.html`

**Results:**
- Total Requests: `_______`
- Requests/Second: `_______` RPS
- P95 Response Time: `_______` ms
- Error Rate: `_______` %

### 2.2 Production Test (if applicable)
- [ ] Run against production URL
- [ ] Document results
- [ ] Compare with baseline

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Step 3: Deploy Monitoring Stack (20 minutes)

### 3.1 Install Prometheus + Grafana
- [ ] Add Helm repo:
  ```bash
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm repo update
  ```
- [ ] Install monitoring stack:
  ```bash
  helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --set grafana.adminPassword='______________'
  ```
- [ ] Wait for pods to be ready:
  ```bash
  kubectl get pods -n monitoring
  ```

**Grafana Admin Password:** `______________`

### 3.2 Access Grafana
- [ ] Port forward to Grafana:
  ```bash
  kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
  ```
- [ ] Visit http://localhost:3000
- [ ] Login with admin / [password from above]
- [ ] Verify Prometheus data source is configured

### 3.3 Import Dashboard
- [ ] Navigate to Dashboards > Import
- [ ] Upload file: `k8s/grafana-dashboard.json`
- [ ] Select Prometheus data source
- [ ] Save dashboard
- [ ] Verify all 8 panels show data

**Dashboard URL:** `_________________________________`

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Step 4: Verify Prometheus Metrics (5 minutes)

### 4.1 Check Metrics Endpoint
- [ ] Test metrics endpoint:
  ```bash
  curl http://localhost:8000/metrics
  ```
- [ ] Verify Prometheus format output
- [ ] Check for custom `realdiag_*` metrics

### 4.2 Verify Prometheus Scraping
- [ ] Port forward to Prometheus:
  ```bash
  kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
  ```
- [ ] Visit http://localhost:9090/targets
- [ ] Verify `realdiag-api` target shows **UP**
- [ ] Check last scrape time is recent

### 4.3 Query Metrics
- [ ] Visit http://localhost:9090/graph
- [ ] Run query: `realdiag_http_requests_total`
- [ ] Verify data returns
- [ ] Test other metrics (see list in completion report)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Step 5: Deploy Alert Rules (10 minutes)

### 5.1 Apply Alert Rules
- [ ] Apply rules to cluster:
  ```bash
  kubectl apply -f k8s/prometheus-rules.yaml -n monitoring
  ```
- [ ] Verify rules created:
  ```bash
  kubectl get prometheusrule -n monitoring
  ```
- [ ] Should see `realdiag-alerts`

### 5.2 Verify in Prometheus
- [ ] Visit http://localhost:9090/alerts
- [ ] Verify 13 RealDiag alert rules visible
- [ ] Check initial state (should be green/inactive)
- [ ] Review alert conditions

**Alert Rules Found:**
- [ ] RealDiagHighErrorRate
- [ ] RealDiagCriticalErrorRate
- [ ] RealDiagHighResponseTime
- [ ] RealDiagVeryHighResponseTime
- [ ] RealDiagHighMemoryUsage
- [ ] RealDiagHighCPUUsage
- [ ] RealDiagPodRestartLoop
- [ ] RealDiagPodNotReady
- [ ] RealDiagDeploymentReplicaMismatch
- [ ] RealDiagHPAMaxedOut
- [ ] RealDiagLowRequestRate
- [ ] RealDiagCertificateExpiringSoon
- [ ] RealDiagHighRateLimitHits

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Step 6: Configure Alert Channels (15 minutes)

### 6.1 Prepare Alert Configuration
- [ ] Copy template from `MONITORING_COMPLETION_REPORT.md`
- [ ] Fill in credentials:
  - [ ] Email SMTP settings
  - [ ] Slack webhook URL
  - [ ] PagerDuty integration key
- [ ] Save as `alertmanager-config.yaml`

**Email:** `_________________________________`  
**Slack Channel:** `_________________________________`  
**PagerDuty Key:** `_________________________________`

### 6.2 Deploy Alertmanager Config
- [ ] Create Kubernetes secret:
  ```bash
  kubectl create secret generic alertmanager-config \
    --from-file=alertmanager.yaml=alertmanager-config.yaml \
    -n monitoring
  ```
- [ ] Restart Alertmanager pod (if needed)
- [ ] Verify secret created:
  ```bash
  kubectl get secret alertmanager-config -n monitoring
  ```

### 6.3 Test Alert Delivery
- [ ] Port forward to Alertmanager:
  ```bash
  kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-alertmanager 9093:9093
  ```
- [ ] Visit http://localhost:9093
- [ ] Trigger test alert (see quick start guide)
- [ ] Verify notification received via:
  - [ ] Email
  - [ ] Slack
  - [ ] PagerDuty (if configured)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Post-Deployment Verification (15 minutes)

### End-to-End Test
- [ ] Generate traffic to application
- [ ] Check Grafana dashboard shows live data
- [ ] Verify Sentry captures errors (if any)
- [ ] Confirm Prometheus scraping metrics
- [ ] Test alert fires correctly (optional)

### Documentation
- [ ] Document performance baselines:
  - P50: `______` ms
  - P95: `______` ms
  - P99: `______` ms
  - Max RPS: `______`
- [ ] Record alert thresholds
- [ ] Update runbooks with actual values
- [ ] Share dashboard URLs with team

### Team Handoff
- [ ] Share Grafana credentials with team
- [ ] Share Sentry login with developers
- [ ] Distribute alert response procedures
- [ ] Schedule dashboard walkthrough meeting

---

## Troubleshooting

### Common Issues

**Sentry not capturing errors:**
- [ ] Check `SENTRY_DSN` environment variable is set
- [ ] Verify backend logs show Sentry initialization
- [ ] Test with `/api/test-error` endpoint
- [ ] Check Sentry project DSN matches

**Grafana shows no data:**
- [ ] Verify Prometheus target is UP
- [ ] Check `/metrics` endpoint is accessible
- [ ] Verify ServiceMonitor is created
- [ ] Check Prometheus scrape config

**Alerts not firing:**
- [ ] Verify alert rules are applied: `kubectl get prometheusrule -n monitoring`
- [ ] Check Alertmanager secret exists
- [ ] Test alert manually via Alertmanager API
- [ ] Verify webhook URLs and credentials

**Load test fails:**
- [ ] Ensure backend server is running
- [ ] Check port 8000 is accessible
- [ ] Verify no firewall blocking traffic
- [ ] Check server logs for errors

---

## Sign-Off

### Deployment Team
- **Deployed by:** _______________  Date: ___/___/___
- **Verified by:** _______________  Date: ___/___/___
- **Approved by:** _______________  Date: ___/___/___

### Completion Confirmation
- [ ] All steps 1-6 marked complete
- [ ] All verification checks passed
- [ ] Team trained on monitoring tools
- [ ] Documentation updated
- [ ] Runbooks created/updated
- [ ] On-call procedures documented

---

## Next Steps (Week 1)

- [ ] Day 1: Monitor dashboards hourly
- [ ] Day 2: Review Sentry errors, tune alert thresholds
- [ ] Day 3: Run additional load tests during peak hours
- [ ] Day 4: Document lessons learned
- [ ] Day 5: Optimize dashboard panels based on usage
- [ ] Week 1 Review: Schedule retrospective meeting

---

**DEPLOYMENT COMPLETE! 🎉**

---

_Checklist based on: MONITORING_COMPLETION_REPORT.md_  
_For detailed instructions, see: MONITORING_QUICK_START.md_  
_Generated: November 21, 2025_
