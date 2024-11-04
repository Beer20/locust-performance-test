from locust import HttpUser, task, between
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class LoadTestUser(HttpUser):
    wait_time = between(1, 3)  # Wait between 1-3 seconds between each task
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_times = []

    def on_start(self):
        """Initialize session for each user"""
        log.info("Starting a new session for user")

    @task(2)
    def fetch_user_info(self):
        """Fetch details for a specific user"""
        user_id = 1  # Sample user ID
        start = time.time()
        
        with self.client.get(f"/users/{user_id}", catch_response=True) as response:
            elapsed_time = time.time() - start
            self.response_times.append(elapsed_time)
            
            try:
                if response.status_code == 200:
                    log.info(f"User {user_id} details fetched in {elapsed_time:.2f} seconds")
                    if elapsed_time > 2.0:  # Log a warning if response time exceeds 2 seconds
                        log.warning(f"Response time exceeded: {elapsed_time:.2f} seconds")
                else:
                    log.error(f"Failed to fetch user {user_id} - Status: {response.status_code}")
                    response.failure(f"Unexpected status code: {response.status_code}")
            except Exception as e:
                log.error(f"Request error: {e}")
                response.failure(f"Request error: {e}")

    @task(1)
    def check_system_status(self):
        """Check the system health endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                log.info("System health is good")
            else:
                log.warning(f"System health check failed - Status: {response.status_code}")

    def on_stop(self):
        """Calculate and log average response time"""
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            max_time = max(self.response_times)
            log.info(f"""\nPerformance Results:\n--------------------\nAverage Response Time: {avg_time:.2f} seconds\nMax Response Time: {max_time:.2f} seconds\nTotal Requests Made: {len(self.response_times)}\n""")

# Locust configuration
class Config:
    host = "https://jsonplaceholder.typicode.com"
    user_count = 10
    spawn_interval = 1
    duration = "1m"
