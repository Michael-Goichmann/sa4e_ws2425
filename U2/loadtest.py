from locust import HttpUser, TaskSet, task, between
import random


class XmasWishesTasks(TaskSet):
    @task
    def create_wish(self):
        # Body = {"name":"TestName","wish":"Some Wish","status":1}
        payload = {
            "name": f"TestUser_{random.randint(1, 1000)}",
            "wish": "LocustPerformanceTest",
        }
        with self.client.post("/wishes", json=payload, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(f"Failed to create wish - Code {response.status_code}")

    # @task
    # def get_all_wishes(self):
    #     # Beispiel: GET /wishes
    #     with self.client.get("/wishes", catch_response=True) as response:
    #         if response.status_code != 200:
    #             response.failure(f"Failed to get wishes - Code {response.status_code}")


class XmasUser(HttpUser):
    tasks = [XmasWishesTasks]
    wait_time = between(1, 2)  # Zeit in Sekunden zwischen zwei Tasks

