from locust import HttpUser, task, between

class ApplicationUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds

    @task
    def retrieve_users(self):
        self.client.get('/users')
