# Production Monitoring - Quick Reference Card

## 🚀 Steps 1-6 Completion Status

### ✅ Step 1: Enable Sentry (5 min)
```bash
# Add to .env
export SENTRY_DSN="https://your-key@sentry.io/project"
export ENVIRONMENT="production"

# Restart app
systemctl restart realdiag-api

# Verify
curl http://localhost:8000/health/detailed | jq .sentry
```

### ✅ Step 2: Run Load Tests (15 min)
```bash
# Baseline test
locust -f tests/locustfile.py \
  --host=http://localhost:8000 \
  --users=50 --spawn-rate=5 \
  --run-time=5m --headless \
  --html=baseline_results.html

# Check results
open baseline_results.html
```

### ✅ Step 3: Create Grafana Dashboard (20 min)
```bash
# Deploy monitoring stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword='SecurePassword123!'

# Port forward to Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Visit http://localhost:3000
# Login: admin / SecurePassword123!
# Import k8s/grafana-dashboard.json
```

### ✅ Step 4: Verify Prometheus Metrics (5 min)
```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Port forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Visit http://localhost:9090/targets
# Verify realdiag-api target is UP
```

### ✅ Step 5: Deploy Alert Rules (10 min)
```bash
# Apply alert rules
kubectl apply -f k8s/prometheus-rules.yaml -n monitoring

# Verify alerts loaded
# Visit http://localhost:9090/alerts
# Should see 13 RealDiag alert rules
```

### ✅ Step 6: Configure Alertmanager (15 min)
```bash
# Create alertmanager config (see MONITORING_COMPLETION_REPORT.md)
kubectl create secret generic alertmanager-config \
  --from-file=alertmanager.yaml=alertmanager-config.yaml \
  -n monitoring

# Test alert
kubectl run test-alert --image=busybox --restart=Never \
  -- sh -c "exit 1"

# Check Alertmanager UI
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-alertmanager 9093:9093
# Visit http://localhost:9093
```

## 📊 Dashboard Access URLs

```bash
# Grafana (Dashboards)
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# → http://localhost:3000

# Prometheus (Metrics & Alerts)
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# → http://localhost:9090

# Alertmanager (Alert Status)
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-alertmanager 9093:9093
# → http://localhost:9093

# Sentry (Error Tracking)
# → https://sentry.io (web-based)

# RealDiag API Metrics
# → http://localhost:8000/metrics
```

## 🎯 Success Criteria

### Sentry
- [  ] Dashboard shows captured errors
- [  ] Performance transactions visible
- [  ] Release tracking shows version
- [  ] Source maps uploaded for frontend

### Load Tests
- [  ] Baseline test completes successfully
- [  ] P95 response time < 500ms
- [  ] Error rate < 0.1%
- [  ] Results documented in HTML report

### Grafana
- [  ] All 8 panels show data
- [  ] Request rate graph trending
- [  ] Error rate gauge < 1%
- [  ] Latency P95/P99 visible

### Prometheus
- [  ] /metrics endpoint returns data
- [  ] realdiag-api target shows UP
- [  ] Custom metrics visible
- [  ] Alert rules loaded (13 total)

### Alertmanager
- [  ] Config secret created
- [  ] Email/Slack channels configured
- [  ] Test alert fires successfully
- [  ] Notifications received

### Integration
- [  ] Sentry captures test error
- [  ] Grafana shows live metrics
- [  ] Alert fires and notifies team
- [  ] Load test validates performance

## ⚡ Common Issues & Solutions

### Sentry Not Capturing Errors
```bash
# Check DSN is set
echo $SENTRY_DSN

# Verify in logs
tail -f /var/log/realdiag/backend.log | grep -i sentry

# Test error endpoint
curl http://localhost:8000/api/test-error
```

### Grafana Shows No Data
```bash
# Check Prometheus target health
kubectl get servicemonitor -n monitoring

# Verify metrics endpoint works
curl http://realdiag-api:8000/metrics

# Check Prometheus scrape config
kubectl get prometheus -n monitoring -o yaml
```

### Alerts Not Firing
```bash
# Verify alert rules applied
kubectl get prometheusrule -n monitoring

# Check Alertmanager config
kubectl get secret alertmanager-config -n monitoring -o yaml

# Test alert manually
curl -H "Content-Type: application/json" -d '[{
  "labels": {"alertname":"TestAlert","severity":"warning"},
  "annotations": {"summary":"Test alert"}
}]' http://localhost:9093/api/v1/alerts
```

### Load Test Fails to Connect
```bash
# Check server is running
curl http://localhost:8000/health

# Verify port is accessible
netstat -an | grep 8000

# Check firewall rules
sudo iptables -L -n | grep 8000
```

## 📋 Total Time Estimate

| Step | Duration | Difficulty |
|------|----------|------------|
| 1. Enable Sentry | 5 min | Easy |
| 2. Run Load Tests | 15 min | Easy |
| 3. Create Grafana Dashboard | 20 min | Medium |
| 4. Verify Prometheus | 5 min | Easy |
| 5. Deploy Alert Rules | 10 min | Easy |
| 6. Configure Alertmanager | 15 min | Medium |
| **Total** | **70 min** | |

## 🎓 Next Steps After Completion

1. **Document Baselines** (30 min)
   - Record P50/P95/P99 latencies
   - Note sustainable RPS
   - Document resource usage

2. **Create Runbooks** (1 hour)
   - Alert response procedures
   - Escalation paths
   - Common troubleshooting steps

3. **Team Training** (2 hours)
   - Dashboard walkthrough
   - Alert interpretation
   - Incident response practice

4. **Optimize Thresholds** (ongoing)
   - Tune alert thresholds based on real traffic
   - Adjust dashboard time ranges
   - Add custom panels for specific use cases

---

**For detailed instructions, see:** `MONITORING_COMPLETION_REPORT.md`

**Infrastructure Status:** ✅ COMPLETE  
**Ready for Production:** YES (after configuration)
