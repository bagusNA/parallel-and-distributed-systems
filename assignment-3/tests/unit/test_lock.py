import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.nodes.base_node import app
import src.nodes.lock_manager  # Ensure endpoints are registered

client = TestClient(app)

@pytest.fixture
def mock_redis():
    with patch("src.nodes.lock_manager.redis_client") as mock:
        yield mock

@pytest.fixture
def mock_raft():
    with patch("src.nodes.lock_manager.raft_node") as mock:
        yield mock

@pytest.fixture
def mock_settings():
    with patch("src.nodes.lock_manager.settings") as mock:
        mock.NODE_TYPE = "lock_manager"
        mock.REDIS_URL = "redis://localhost"
        yield mock

def test_acquire_lock_success(mock_redis, mock_raft, mock_settings):
    mock_raft.propose = AsyncMock(return_value=(True, "node_1"))
    mock_redis.set = AsyncMock(return_value=True)
    
    response = client.post("/lock/acquire", json={
        "resource_id": "item_1",
        "owner_id": "user_1"
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "acquired"

def test_acquire_lock_failure_already_held(mock_redis, mock_raft, mock_settings):
    mock_raft.propose = AsyncMock(return_value=(True, "node_1"))
    mock_redis.set = AsyncMock(return_value=False)
    
    response = client.post("/lock/acquire", json={
        "resource_id": "item_1",
        "owner_id": "user_2"
    })
    
    assert response.status_code == 409
    assert "already acquired" in response.json()["detail"]

def test_release_lock_success(mock_redis, mock_raft, mock_settings):
    mock_raft.propose = AsyncMock(return_value=(True, "node_1"))
    mock_redis.eval = AsyncMock(return_value=1)
    
    response = client.post("/lock/release", json={
        "resource_id": "item_1",
        "owner_id": "user_1"
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "released"

def test_release_lock_fail_not_owner(mock_redis, mock_raft, mock_settings):
    mock_raft.propose = AsyncMock(return_value=(True, "node_1"))
    mock_redis.eval = AsyncMock(return_value=0)
    
    response = client.post("/lock/release", json={
        "resource_id": "item_1",
        "owner_id": "user_2"
    })
    
    assert response.status_code == 400
    assert "Not lock owner" in response.json()["detail"]
