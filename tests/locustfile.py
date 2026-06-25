"""
Load Testing with Locust
Performance and scalability testing scenarios
"""

from locust import HttpUser, task, between, events
import random
import json


class RealDiagUser(HttpUser):
    """Simulate a typical RealDiag user"""
    
    # Wait 1-3 seconds between tasks
    wait_time = between(1, 3)
    
    # Sample test data
    symptoms_list = [
        ["chest pain", "shortness of breath"],
        ["headache", "dizziness", "nausea"],
        ["abdominal pain", "fever"],
        ["cough", "fever", "fatigue"],
        ["joint pain", "swelling"]
    ]
    
    specialties = [
        "neurology",
        "cardiology",
        "endocrinology",
        "pulmonology",
        "gastroenterology"
    ]
    
    def on_start(self):
        """Called when a user starts"""
        # Simulate user arriving at site
        self.client.get("/")
    
    @task(3)
    def symptom_search(self):
        """Perform symptom search - most common task"""
        symptoms = random.choice(self.symptoms_list)
        payload = {
            "symptoms": symptoms,
            "age": random.randint(20, 80),
            "sex": random.choice(["M", "F"])
        }
        
        with self.client.post(
            "/search/by-symptoms",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    response.success()
                else:
                    response.failure("No results in response")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def browse_reference(self):
        """Browse diagnostic reference"""
        family = random.choice(self.specialties)
        
        with self.client.get(
            f"/reference/{family}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "rules" in data and len(data["rules"]) > 0:
                    response.success()
                else:
                    response.failure("No rules in response")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def view_education_cases(self):
        """View education cases"""
        with self.client.get(
            "/education/cases",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def search_education_cases(self):
        """Search education cases"""
        query = random.choice(["chest pain", "headache", "diabetes", "hypertension"])
        
        with self.client.get(
            f"/education/cases/search/{query}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_quiz_questions(self):
        """Get quiz questions"""
        with self.client.get(
            "/education/quiz/questions?count=5",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Check system health"""
        with self.client.get(
            "/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class PowerUser(HttpUser):
    """Simulate a power user making many requests"""
    
    wait_time = between(0.5, 1)
    
    @task
    def rapid_searches(self):
        """Perform rapid symptom searches"""
        for _ in range(3):
            symptoms = random.sample([
                "chest pain", "headache", "fever", "cough",
                "nausea", "fatigue", "dizziness"
            ], k=random.randint(1, 4))
            
            self.client.post(
                "/search/by-symptoms",
                json={"symptoms": symptoms}
            )


class APIUser(HttpUser):
    """Simulate API-only user (integration)"""
    
    wait_time = between(2, 5)
    
    @task
    def api_batch_request(self):
        """Simulate batch API requests"""
        # Get multiple references
        for family in ["cardiology", "neurology", "pulmonology"]:
            self.client.get(f"/reference/{family}")


# Event handlers for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("Load test completed")
    
    # Print summary
    stats = environment.stats
    print("\n=== Load Test Summary ===")
    print(f"Total requests: {stats.num_requests}")
    print(f"Total failures: {stats.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.total_rps:.2f}")
