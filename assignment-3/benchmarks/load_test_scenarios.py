from locust import HttpUser, task, between
import random
import uuid

class FlashSaleUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def buy_item(self):
        # We simulate a flash sale where many users try to buy limited items
        item_id = f"item_{random.randint(1, 10)}"
        user_id = str(uuid.uuid4())
        
        # 1. Acquire Lock
        lock_manager_node = f"http://localhost:800{random.randint(1, 3)}"
        lock_payload = {
            "resource_id": item_id,
            "owner_id": user_id,
            "timeout": 5000
        }
        
        with self.client.post(f"{lock_manager_node}/lock/acquire", json=lock_payload, catch_response=True) as lock_res:
            if lock_res.status_code == 200:
                # 2. Check Cache
                cache_node = f"http://localhost:802{random.randint(1, 3)}"
                with self.client.get(f"{cache_node}/cache/{item_id}_stock", catch_response=True) as cache_res:
                    stock = 0
                    if cache_res.status_code == 200:
                        stock = cache_res.json().get("value", 0)
                    elif cache_res.status_code == 404:
                        # Initialize stock for the demo
                        stock = 100
                        self.client.post(f"{cache_node}/cache/{item_id}_stock", json={"value": stock, "version": 1})
                        
                    if stock > 0:
                        # 3. Decrement Stock
                        self.client.post(f"{cache_node}/cache/{item_id}_stock", json={"value": stock - 1, "version": 2})
                        
                        # 4. Push to Queue
                        queue_node = f"http://localhost:801{random.randint(1, 3)}"
                        order_payload = {
                            "topic": "orders",
                            "message": {"item_id": item_id, "user_id": user_id}
                        }
                        self.client.post(f"{queue_node}/queue/publish", json=order_payload)
                        
                # 5. Release Lock
                release_payload = {
                    "resource_id": item_id,
                    "owner_id": user_id
                }
                self.client.post(f"{lock_manager_node}/lock/release", json=release_payload)
            elif lock_res.status_code in [307, 409]:
                # Lock contention or redirect, mark as failure or ignore
                lock_res.success()

class ThroughputScalingUser(HttpUser):
    wait_time = between(0, 0.1) # High frequency

    @task
    def health_check(self):
        node = f"http://localhost:800{random.randint(1, 3)}"
        self.client.get(f"{node}/health")

class LockContentionUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task
    def heavy_contention(self):
        # All users hit SAME item
        item_id = "hot_item_1"
        user_id = str(uuid.uuid4())
        node = "http://localhost:8001"
        
        self.client.post(f"{node}/lock/acquire", json={
            "resource_id": item_id,
            "owner_id": user_id
        })
        self.client.post(f"{node}/lock/release", json={
            "resource_id": item_id,
            "owner_id": user_id
        })
