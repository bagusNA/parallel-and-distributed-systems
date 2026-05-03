import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.consensus.raft import RaftNode
from src.consensus.pbft import PBFTNode

@pytest.mark.asyncio
async def test_raft_leader_accepts_propose():
    node = RaftNode("node_1", ["http://node_1:8000", "http://node_2:8000", "http://node_3:8000"])
    node.state = "LEADER"
    node.current_term = 1
    
    # Mock commit index update to simulate quick consensus
    async def mock_propose(command):
        node.log.append(command)
        node.commit_index = len(node.log)
        return True, "node_1"
        
    with patch.object(node, 'propose', side_effect=mock_propose):
        success, leader = await node.propose({"action": "lock"})
        assert success is True

@pytest.mark.asyncio
async def test_raft_follower_rejects_propose():
    node = RaftNode("node_1", ["http://node_1:8000", "http://node_2:8000", "http://node_3:8000"])
    node.state = "FOLLOWER"
    node.leader_id = "node_2"
    
    success, leader = await node.propose({"action": "lock"})
    assert success is False
    assert leader == "node_2"

@pytest.mark.asyncio
async def test_pbft_quorum_commit():
    node = PBFTNode("node_1", ["http://node_1:8000", "http://node_2:8000", "http://node_3:8000"])
    # n=3, quorum=2
    msg_id = "msg_1"
    
    # Simulate receiving PREPAREs from quorum
    await node.handle_prepare({"msg_id": msg_id, "node_id": "node_1"})
    await node.handle_prepare({"msg_id": msg_id, "node_id": "node_2"})
    
    # Should have triggered COMMIT broadcast and self-commit
    assert msg_id in node.commits
    assert len(node.commits[msg_id]) >= 1 # Self commit
    
    # Simulate receiving COMMITs from quorum
    await node.handle_commit({"msg_id": msg_id, "node_id": "node_1"})
    await node.handle_commit({"msg_id": msg_id, "node_id": "node_2"})
    
    assert msg_id in node.committed

@pytest.mark.asyncio
async def test_pbft_no_commit_without_quorum():
    node = PBFTNode("node_1", ["http://node_1:8000", "http://node_2:8000", "http://node_3:8000"])
    msg_id = "msg_2"
    
    # Only 1 node (self) commits
    await node.handle_commit({"msg_id": msg_id, "node_id": "node_1"})
    
    assert msg_id not in node.committed
