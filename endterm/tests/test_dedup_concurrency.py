import os
import pytest
import asyncio
from fastapi.testclient import TestClient


# Set up test environment
os.environ["DATABASE_URL"] = "sqlite:///appdata/database/test_dedup_concurrency.db"
from src.main import app
from src.database import Base, engine, SessionLocal, ProcessedEvent
from src.models import Event
from src.aggregator import aggregator
from src.migration import init_db

client = TestClient(app)

@pytest.mark.asyncio
async def test_dedup_concurrency():
    """Publish the same event concurrently from multiple workers and ensure only one is processed."""
    event = {
        "topic": "concurrent_topic",
        "event_id": "conc_1",
        "timestamp": "2024-01-01T00:00:00Z",
        "source": "test_src",
        "payload": {"data": "value"},
    }
    workers = 4

    async def publish():
        aggregator._persist_event(Event(**event))

    await asyncio.gather(*[publish() for _ in range(workers)])

    # After all publishes, only one unique should be counted
    assert aggregator.unique_processed_count == 1
    assert aggregator.duplicate_dropped_count == workers
