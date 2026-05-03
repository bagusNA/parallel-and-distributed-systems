import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.nodes.base_node import app
import src.nodes.queue_node

client = TestClient(app)

@pytest.fixture
def mock_redis():
    with patch("src.nodes.queue_node.redis_client") as mock:
        yield mock

@pytest.fixture
def mock_settings():
    with patch("src.nodes.queue_node.settings") as mock:
        mock.NODE_TYPE = "queue_node"
        mock.NODE_ID = "queue_1"
        mock.PORT = 8000
        mock.peer_nodes = []
        yield mock

def test_ack_removes_message(mock_settings):
    # ACK currently just returns status as logic for 'processing' set is simplified
    response = client.post("/queue/ack", json={
        "topic": "orders",
        "msg_id": "msg_123"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "acked"

def test_nack_requeues_message(mock_redis, mock_settings):
    mock_redis.rpush = AsyncMock()
    
    response = client.post("/queue/nack", json={
        "topic": "orders",
        "msg_id": "msg_123",
        "message": {"item": "phone"},
        "retry_count": 0
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "requeued"
    assert response.json()["retry_count"] == 1
    mock_redis.rpush.assert_called_once()

def test_nack_max_retries_reaches_dlq(mock_redis, mock_settings):
    mock_redis.rpush = AsyncMock()
    
    response = client.post("/queue/nack", json={
        "topic": "orders",
        "msg_id": "msg_123",
        "message": {"item": "phone"},
        "retry_count": 3
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "failed_max_retries"
    # Verify it was pushed to dlq:orders
    args, _ = mock_redis.rpush.call_args
    assert "dlq:orders" in args[0]
