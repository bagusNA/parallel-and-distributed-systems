import os
import pytest
from fastapi.testclient import TestClient

# Set up test environment
os.environ["DATABASE_URL"] = "sqlite:///appdata/database/test_stats_consistency.db"
from src.main import app
from src.database import Base, engine, SessionLocal, ProcessedEvent
from src.aggregator import aggregator
from src.migration import init_db

client = TestClient(app)

@pytest.mark.parametrize("num_events", [5, 10, 20])
def test_stats_and_events_consistency(num_events):
    """Publish a batch of events and verify /stats and /events are consistent."""
    # Publish events
    batch = [
        {
            "topic": f"topic_{i}",
            "event_id": f"id_{i}",
            "timestamp": "2024-01-01T00:00:00Z",
            "source": "test_src",
            "payload": {}
        }
        for i in range(num_events)
    ]
    response = client.post("/publish", json=batch)
    assert response.status_code == 200
    assert response.json()["processed_count"] == num_events

    # Verify stats endpoint reflects the counts
    stats_resp = client.get("/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    # "received" counts total publishes (including batch request as one), but we care about unique_processed
    assert stats.get("unique_processed", 0) >= num_events

    # Verify events endpoint returns the same number of unique events
    events_resp = client.get("/events")
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert isinstance(events, list)
    # At least the number we just published should be present
    assert len(events) >= num_events
