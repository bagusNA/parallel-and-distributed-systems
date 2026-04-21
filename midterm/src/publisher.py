import time
import requests
import random
import uuid
from datetime import datetime, timezone

AGGREGATOR_URL = "http://aggregator:8080"
TOTAL_EVENTS = 5000
DUPLICATE_PROBABILITY = 0.2

def generate_event(event_id=None, topic=None):
    return {
        "topic": topic or random.choice(["orders", "inventory", "notifications"]),
        "event_id": event_id or str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "simulated_publisher",
        "payload": {"data": random.randint(1, 1000)}
    }

def run_simulation():
    print(f"Starting simulation. Target events: {TOTAL_EVENTS}")
    
    unique_events = []
    sent_count = 0
    duplicate_count = 0
    
    # Wait for aggregator to be ready
    for _ in range(10):
        try:
            resp = requests.get(f"{AGGREGATOR_URL}/health")
            if resp.status_code == 200:
                print("Aggregator is ready.")
                break
        except:
            print("Waiting for aggregator...")
            time.sleep(2)
    else:
        print("Aggregator not reachable. Exiting.")
        return

    for i in range(TOTAL_EVENTS):
        # Decide if we send a new event or a duplicate
        if unique_events and random.random() < DUPLICATE_PROBABILITY:
            # Send a duplicate
            event = random.choice(unique_events)
            duplicate_count += 1
        else:
            # Send a new event
            event = generate_event()
            unique_events.append(event)
        
        try:
            # Randomly batch 1-10 events or send single
            if random.random() < 0.1: # Batch
                batch = [event]
                for _ in range(random.randint(1, 9)):
                    batch.append(generate_event())
                resp = requests.post(f"{AGGREGATOR_URL}/publish", json=batch)
                sent_count += len(batch)
            else:
                resp = requests.post(f"{AGGREGATOR_URL}/publish", json=event)
                sent_count += 1
                
            if i % 500 == 0:
                print(f"Progress: {i}/{TOTAL_EVENTS} events sent.")
        except Exception as e:
            print(f"Error sending event: {e}")

    print(f"Simulation complete. Sent: {sent_count}, Intended duplicates: {duplicate_count}")
    
    # Final check
    time.sleep(5) # Give worker time to finish
    try:
        resp = requests.get(f"{AGGREGATOR_URL}/stats")
        print("Final Stats from Aggregator:")
        print(resp.json())
    except Exception as e:
        print(f"Could not fetch stats: {e}")

if __name__ == "__main__":
    run_simulation()
