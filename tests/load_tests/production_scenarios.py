"""
Load Testing Scenarios for RealDiag Production
===============================================

This module defines comprehensive load testing scenarios to validate
production performance and autoscaling behavior.

Usage:
    # Basic load test
    locust -f tests/load_tests/production_scenarios.py --host=https://api.realdiag.com

    # Headless with specific user count
    locust -f tests/load_tests/production_scenarios.py --host=https://api.realdiag.com \
           --users 100 --spawn-rate 10 --run-time 10m --headless

    # Test autoscaling
    locust -f tests/load_tests/production_scenarios.py --host=https://api.realdiag.com \
           --users 500 --spawn-rate 20 --run-time 30m --headless
"""

from locust import HttpUser, task, between, events
import random
import json
import time


class RealDiagUser(HttpUser):
    """Simulates a typical RealDiag user workflow"""
    
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks
    
    def on_start(self):
        """Initialize user session"""
        self.symptoms = [
            "headache",
            "fever",
            "cough",
            "fatigue",
            "nausea",
            "dizziness",
            "chest pain",
            "shortness of breath",
            "abdominal pain",
        ]
        self.diagnostic_trees = ["NEU-HEADACHE", "NEU-VERTIGO"]
        self.user_token = None
    
    @task(5)
    def view_homepage(self):
        """User visits the homepage (most common action)"""
        with self.client.get("/", catch_response=True, name="Homepage") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Homepage returned {response.status_code}")
    
    @task(10)
    def search_symptoms(self):
        """User searches for symptoms (very common)"""
        symptom = random.choice(self.symptoms)
        with self.client.get(
            f"/api/symptoms/search?q={symptom}",
            catch_response=True,
            name="Search Symptoms"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "results" in data:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Search returned {response.status_code}")
    
    @task(3)
    def start_diagnostic(self):
        """User starts a diagnostic tree"""
        tree = random.choice(self.diagnostic_trees)
        with self.client.post(
            "/api/diagnostic/start",
            json={"tree_id": tree},
            catch_response=True,
            name="Start Diagnostic"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Diagnostic start returned {response.status_code}")
    
    @task(2)
    def get_diagnostic_trees(self):
        """User views available diagnostic trees"""
        with self.client.get(
            "/api/diagnostic/trees",
            catch_response=True,
            name="List Diagnostic Trees"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Tree list returned {response.status_code}")
    
    @task(2)
    def view_references(self):
        """User browses medical references"""
        with self.client.get(
            "/api/references",
            catch_response=True,
            name="View References"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"References returned {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Monitoring/health check (low frequency)"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="Health Check"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with {response.status_code}")


class AuthenticatedUser(HttpUser):
    """Simulates authenticated user workflows"""
    
    wait_time = between(3, 8)
    
    def on_start(self):
        """Login and initialize session"""
        self.login()
    
    def login(self):
        """Simulate user login"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": f"loadtest{random.randint(1, 1000)}@example.com",
                "password": "TestPassword123!"
            },
            catch_response=True,
            name="Login"
        )
        
        if response.status_code in [200, 201]:
            # Store auth token if available
            if "token" in response.json():
                self.token = response.json()["token"]
        # Note: May fail if user doesn't exist, which is expected in load testing
    
    @task(5)
    def view_dashboard(self):
        """Authenticated user views their dashboard"""
        with self.client.get(
            "/api/user/dashboard",
            catch_response=True,
            name="User Dashboard"
        ) as response:
            if response.status_code in [200, 401]:
                # 401 is acceptable (user might not be logged in)
                response.success()
            else:
                response.failure(f"Dashboard returned {response.status_code}")
    
    @task(3)
    def view_history(self):
        """User views their search history"""
        with self.client.get(
            "/api/user/history",
            catch_response=True,
            name="View History"
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"History returned {response.status_code}")
    
    @task(2)
    def save_favorite(self):
        """User saves a diagnostic to favorites"""
        with self.client.post(
            "/api/user/favorites",
            json={
                "tree_id": "NEU-HEADACHE",
                "title": "Headache Diagnostic"
            },
            catch_response=True,
            name="Save Favorite"
        ) as response:
            if response.status_code in [200, 201, 401]:
                response.success()
            else:
                response.failure(f"Save favorite returned {response.status_code}")


class HighLoadSpike(HttpUser):
    """Simulates sudden traffic spikes to test autoscaling"""
    
    wait_time = between(0.5, 2)  # Faster requests to create load
    
    @task(20)
    def rapid_search(self):
        """Rapid symptom searches"""
        symptom = random.choice(["headache", "fever", "cough", "pain"])
        self.client.get(f"/api/symptoms/search?q={symptom}", name="Rapid Search")
    
    @task(10)
    def rapid_health_checks(self):
        """Multiple health checks"""
        self.client.get("/health", name="Rapid Health Check")
    
    @task(5)
    def rapid_api_calls(self):
        """Various API endpoints"""
        endpoints = ["/api/diagnostic/trees", "/api/references", "/version"]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint, name="Rapid API Call")


# Custom events for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start"""
    print("=" * 80)
    print("🚀 RealDiag Production Load Test Starting")
    print(f"   Target: {environment.host}")
    print(f"   Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'Unknown'}")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test results"""
    print("=" * 80)
    print("🏁 RealDiag Production Load Test Completed")
    
    stats = environment.stats
    print(f"\n📊 Summary Statistics:")
    print(f"   Total Requests: {stats.total.num_requests}")
    print(f"   Total Failures: {stats.total.num_failures}")
    print(f"   Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"   Min Response Time: {stats.total.min_response_time:.2f}ms")
    print(f"   Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"   Requests/sec: {stats.total.current_rps:.2f}")
    
    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"   Failure Rate: {failure_rate:.2f}%")
        
        if failure_rate > 5:
            print("\n⚠️  WARNING: Failure rate exceeds 5%")
        elif failure_rate > 1:
            print("\n⚠️  NOTICE: Failure rate exceeds 1%")
        else:
            print("\n✅ Success: Failure rate within acceptable range")
    
    print("=" * 80)


# Load test scenarios configuration
"""
Recommended Load Test Scenarios:

1. **Baseline Test** (Validate normal operation)
   locust -f production_scenarios.py --host=https://api.realdiag.com \
          --users 50 --spawn-rate 5 --run-time 10m --headless

2. **Moderate Load** (Test with expected traffic)
   locust -f production_scenarios.py --host=https://api.realdiag.com \
          --users 200 --spawn-rate 10 --run-time 30m --headless

3. **Peak Load** (Test autoscaling)
   locust -f production_scenarios.py --host=https://api.realdiag.com \
          --users 500 --spawn-rate 20 --run-time 30m --headless

4. **Stress Test** (Find breaking point)
   locust -f production_scenarios.py --host=https://api.realdiag.com \
          --users 1000 --spawn-rate 50 --run-time 15m --headless

5. **Spike Test** (Test sudden traffic increase)
   locust -f production_scenarios.py --host=https://api.realdiag.com \
          --users 100 --spawn-rate 100 --run-time 5m --headless

Monitoring During Tests:
- Watch HPA scaling: kubectl get hpa -n production -w
- Monitor pod count: kubectl get pods -n production -w
- Check Grafana dashboard for golden signals
- Monitor Sentry for error spikes
- Check Prometheus alerts

Success Criteria:
✅ Error rate < 1%
✅ p95 response time < 500ms
✅ p99 response time < 1s
✅ HPA scales up within 2 minutes under load
✅ HPA scales down gracefully after load decreases
✅ No pod crashes or restarts
✅ No critical alerts triggered
"""
