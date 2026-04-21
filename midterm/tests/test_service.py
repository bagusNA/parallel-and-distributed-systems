import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import shutil
from datetime import datetime, timezone

# Set up test environment
os.environ["DATABASE_URL"] = "sqlite:///./test_events.db"
from main import app
from database import Base, engine, SessionLocal, init_db, ProcessedEvent
from aggregator import aggregator

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Clear DB before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Reset aggregator stats
    aggregator.received_count = 0
    aggregator.unique_processed_count = 0
    aggregator.duplicate_dropped_count = 0
    # Clear queue (re-create it)
    import asyncio
    aggregator.queue = asyncio.Queue()
    yield
    # Cleanup
    if os.path.exists("./test_events.db"):
        os.remove("./test_events.db")

def test_schema_validation_invalid():
    # Missing required field 'source'
    invalid_event = {
        "topic": "test",
        "event_id": "1",
        "timestamp": "2024-03-20T10:00:00Z",
        "payload": {}
    }
    response = client.post("/publish", json=invalid_event)
    assert response.status_code == 422 # FastAPI validation error

def test_publish_single_event():
    event = {
        "topic": "test",
        "event_id": "1",
        "timestamp": "2024-03-20T10:00:00Z",
        "source": "test_src",
        "payload": {"data": "hello"}
    }
    response = client.post("/publish", json=event)
    assert response.status_code == 200
    assert response.json()["processed_count"] == 1

@pytest.mark.asyncio
async def test_deduplication():
    event = {
        "topic": "dedup_topic",
        "event_id": "unique_1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "test_src",
        "payload": {}
    }
    
    # Process once manually to skip background worker async delay in unit test
    aggregator._persist_event(aggregator.enqueue_events.__annotations__['events'](**event) if hasattr(aggregator.enqueue_events, '__annotations__') else type('Event', (), event))
    # Wait, better to use the aggregator class directly or mock the background worker
    # Let's just use the persistence logic directly for testing the core logic
    from models import Event
    ev_obj = Event(**event)
    
    aggregator._persist_event(ev_obj)
    assert aggregator.unique_processed_count == 1
    assert aggregator.duplicate_dropped_count == 0
    
    # Process duplicate
    aggregator._persist_event(ev_obj)
    assert aggregator.unique_processed_count == 1
    assert aggregator.duplicate_dropped_count == 1

def test_persistence_across_restarts():
    event_data = {
        "topic": "persist",
        "event_id": "p1",
        "timestamp": datetime.now(timezone.utc),
        "source": "test_src",
        "payload": {}
    }
    
    # 1. Save event to DB
    db = SessionLocal()
    ev = ProcessedEvent(**event_data)
    db.add(ev)
    db.commit()
    db.close()
    
    # 2. Simulate "Restart" by creating a new Aggregator instance
    from aggregator import EventAggregator
    new_aggregator = EventAggregator()
    assert new_aggregator.unique_processed_count == 1
    
    # 3. Try to drop same event
    from models import Event
    ev_obj = Event(
        topic=event_data["topic"],
        event_id=event_data["event_id"],
        timestamp=event_data["timestamp"],
        source=event_data["source"],
        payload=event_data["payload"]
    )
    new_aggregator._persist_event(ev_obj)
    assert new_aggregator.unique_processed_count == 1
    assert new_aggregator.duplicate_dropped_count == 1

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "received" in data
    assert "unique_processed" in data
    assert "duplicate_dropped" in data

def test_batch_ingestion():
    batch = [
        {
            "topic": "batch",
            "event_id": f"id_{i}",
            "timestamp": "2024-03-20T10:00:00Z",
            "source": "test",
            "payload": {}
        } for i in range(5)
    ]
    response = client.post("/publish", json=batch)
    assert response.status_code == 200
    assert response.json()["processed_count"] == 5
