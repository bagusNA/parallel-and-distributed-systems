import os
import pytest
from fastapi.testclient import TestClient

# Set up test environment
os.environ["DATABASE_URL"] = "sqlite:///appdata/database/test_schema_additional.db"
from src.main import app
from src.database import Base, engine, SessionLocal, ProcessedEvent
from src.aggregator import aggregator
from src.migration import init_db

client = TestClient(app)

@pytest.mark.parametrize("event,missing_field", [
    ({
        "topic": "test",
        "event_id": "1",
        "timestamp": "2024-03-20T10:00:00Z",
        "payload": {}
    }, "source"),
    ({
        "topic": "test",
        "source": "src",
        "timestamp": "2024-03-20T10:00:00Z",
        "payload": {}
    }, "event_id"),
    ({
        "source": "src",
        "event_id": "1",
        "timestamp": "2024-03-20T10:00:00Z",
        "payload": {}
    }, "topic")
])
def test_schema_missing_required_field(event, missing_field):
    response = client.post("/publish", json=event)
    assert response.status_code == 422

# def test_invalid_timestamp_type():
#     event = {
#         "topic": "test",
#         "event_id": "1",
#         "timestamp": 123456,  # invalid type, should be string ISO8601
#         "source": "src",
#         "payload": {}
#     }
#     response = client.post("/publish", json=event)
#     assert response.status_code == 422
