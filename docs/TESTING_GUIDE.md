# Quality & Performance Testing Guide

## 📋 Overview

This guide covers all quality and performance testing tools implemented in RealDiag-Software.

## 🧪 Unit Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_symptom_search.py -v

# Run specific test
pytest tests/test_health.py::test_health_endpoint -v
```

### Test Coverage

Current test coverage: **>50%** backend coverage

Test files:
- `tests/test_health.py` - Health checks and basic endpoints
- `tests/test_symptom_search.py` - Symptom search functionality
- `tests/test_reference.py` - Diagnostic reference endpoints
- `tests/test_education.py` - Education features
- `tests/conftest.py` - Shared fixtures

### Writing New Tests

```python
def test_my_endpoint(test_client: TestClient):
    """Test description"""
    response = test_client.get("/my-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## 🎭 End-to-End Testing

### Setup Playwright

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Run E2E tests
pytest tests/test_e2e_playwright.py -v -s
```

### E2E Test Workflows

1. **Symptom Search Workflow** - Complete symptom search flow
2. **Diagnostic Workflow** - Decision tree navigation
3. **Education Workflow** - Clinical cases and quizzes
4. **Account Workflow** - User authentication
5. **Integration Workflow** - EHR connections

### Creating E2E Tests

```python
@pytest.mark.skip(reason="Requires live frontend")
def test_my_workflow(page: Page):
    page.goto("http://localhost:3000/my-page")
    expect(page.locator("h1")).to_contain_text("Expected Title")
    page.click('button:has-text("Submit")')
    expect(page.locator('[data-testid="result"]')).to_be_visible()
```

## 📊 Performance Profiling

### Enable Profiling

Add to `backend/main.py`:

```python
from backend.services.profiling import PerformanceProfiler

# Add middleware
app.add_middleware(
    PerformanceProfiler,
    threshold_ms=1000,  # Log requests slower than 1s
    enable_detailed=True  # Enable cProfile for very slow requests
)
```

### View Performance Reports

```bash
# Get slow requests summary
curl http://localhost:8000/performance/summary

# Get slowest endpoints
curl http://localhost:8000/performance/slow-requests
```

### Manual Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## 🔥 Load Testing with Locust

### Running Load Tests

```bash
# Install Locust
pip install locust

# Start Locust web UI
locust -f tests/locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
# Configure: 100 users, 10 spawn rate

# Run headless
locust -f tests/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless
```

### Load Test Scenarios

1. **RealDiagUser** - Typical user behavior
   - Symptom searches (most common)
   - Reference browsing
   - Education features
   
2. **PowerUser** - High-frequency usage
   - Rapid searches
   - Batch requests
   
3. **APIUser** - Integration clients
   - API-only requests
   - Batch operations

### Interpreting Results

Key metrics:
- **RPS** (Requests Per Second) - Target: >50
- **Response Time** - 50th percentile <200ms, 95th <1000ms
- **Failure Rate** - Target: <1%

### Performance Benchmarks

| Endpoint | Target Response Time | Target RPS |
|----------|---------------------|------------|
| /health | <50ms | 1000+ |
| /search/by-symptoms | <200ms | 100 |
| /reference/{family} | <100ms | 200 |
| /education/cases | <150ms | 100 |

## 🐛 Error Tracking with Sentry

### Setup Sentry

1. Create account at https://sentry.io
2. Get your DSN
3. Set environment variable:

```bash
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
export SENTRY_TRACES_SAMPLE_RATE="0.1"
export ENVIRONMENT="production"
```

### Using Error Tracking

```python
from backend.services.error_tracking import capture_exception, capture_message

try:
    # Your code
    risky_operation()
except Exception as e:
    capture_exception(e, context={
        "user_id": user_id,
        "operation": "risky_operation"
    })
```

### Sentry Features

- **Error Grouping** - Automatic error deduplication
- **Stack Traces** - Full Python stack traces
- **Breadcrumbs** - Request/response history
- **Performance Monitoring** - Transaction tracking
- **Alerts** - Email/Slack notifications

## 📈 Monitoring and Metrics

### Prometheus Metrics

Access metrics:
```bash
curl http://localhost:8000/metrics
```

Available metrics:
- `realdiag_requests_total` - Total HTTP requests
- `realdiag_request_duration_seconds` - Request duration histogram
- `realdiag_active_requests` - Active requests gauge
- `realdiag_symptom_searches_total` - Symptom searches counter
- `realdiag_cpu_usage_percent` - CPU usage
- `realdiag_memory_usage_bytes` - Memory usage

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health with system metrics
curl http://localhost:8000/health/detailed

# Kubernetes liveness probe
curl http://localhost:8000/health/liveness

# Kubernetes readiness probe
curl http://localhost:8000/health/readiness
```

### Structured Logging

Logs include:
- Timestamp (UTC)
- Request method and path
- Response status code
- Duration in milliseconds
- Client IP and user agent
- Error context

## 🔒 Security Auditing

### Running Security Audit

```bash
# Full security audit
python backend/services/security_audit.py

# Output: security_audit_report.json
```

### OWASP Top 10 Checks

The audit checks for:

1. **A01 - Broken Access Control**
   - Missing authentication decorators
   - Unprotected routes

2. **A02 - Cryptographic Failures**
   - Hardcoded secrets
   - Weak encryption

3. **A03 - Injection**
   - SQL injection risks
   - Command injection

4. **A04 - Insecure Design**
   - Manual review required

5. **A05 - Security Misconfiguration**
   - Debug mode enabled
   - Default credentials

6. **A06 - Vulnerable Components**
   - Dependency scanning

7. **A07 - Authentication Failures**
   - Weak password requirements
   - Missing rate limiting

8. **A08 - Data Integrity Failures**
   - Missing validation

9. **A09 - Logging Failures**
   - Missing logging

10. **A10 - SSRF**
    - Unvalidated URL requests

### Dependency Scanning

```bash
# Install pip-audit
pip install pip-audit

# Scan for vulnerabilities
pip-audit --format json > vulnerabilities.json

# Or use safety
safety check --json
```

### Code Security Linting

```bash
# Install bandit
pip install bandit

# Run security linter
bandit -r backend/ -f json -o bandit_report.json

# Check specific files
bandit backend/services/security.py
```

### Secret Scanning

The security audit automatically scans for:
- AWS access keys
- API keys
- Passwords
- Private keys
- OAuth tokens

**Never commit secrets!** Use environment variables.

## 📊 Continuous Integration

### GitHub Actions Workflow

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests with coverage
        run: |
          pytest tests/ --cov=backend --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
      
      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r backend/
          safety check
```

## 🎯 Performance Optimization Tips

### Database Queries
- Add indexes on frequently queried fields
- Use query result caching
- Implement pagination for large datasets
- Avoid N+1 queries

### API Responses
- Enable gzip compression
- Implement response caching
- Use CDN for static assets
- Minimize payload size

### Backend
- Use async/await for I/O operations
- Implement connection pooling
- Enable HTTP/2
- Use background tasks for heavy operations

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Service workers

## 📝 Best Practices

### Testing
✅ Write tests for all new features
✅ Maintain >80% code coverage
✅ Include edge cases and error scenarios
✅ Use meaningful test names
✅ Mock external dependencies

### Performance
✅ Monitor response times
✅ Set performance budgets
✅ Profile slow operations
✅ Optimize database queries
✅ Use caching strategically

### Security
✅ Run security audits regularly
✅ Keep dependencies updated
✅ Never commit secrets
✅ Validate all inputs
✅ Use HTTPS in production

### Monitoring
✅ Track key metrics
✅ Set up alerts
✅ Review error reports
✅ Monitor resource usage
✅ Analyze user behavior

## 🆘 Troubleshooting

### Tests Failing
1. Check test database is clean
2. Verify fixtures are correct
3. Ensure dependencies are installed
4. Check for port conflicts

### Slow Performance
1. Check database indexes
2. Review slow query logs
3. Profile the code
4. Check for memory leaks
5. Verify caching is working

### High Error Rates
1. Check Sentry dashboard
2. Review application logs
3. Verify external dependencies
4. Check resource limits
5. Review recent deployments

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Locust Documentation](https://docs.locust.io/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
