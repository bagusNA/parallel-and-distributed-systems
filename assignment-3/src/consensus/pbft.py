import asyncio
import logging
import time
from typing import Dict, Any, List
from src.utils.config import settings
from src.communication.message_passing import rpc_client

logger = logging.getLogger(__name__)

class PBFTNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        # Peers list includes self, because we might count self vote
        self.all_nodes = peers
        self.peers = [p for p in peers if p != f"http://{node_id}:{settings.PORT}"]
        
        self.f = max((len(self.all_nodes) - 1) // 3, 0)
        # Required quorum: 2f + 1 (For 3 nodes, f=0 is technically standard, but let's assume f=1 so 2f+1=3? Wait, n=3 => f=0. Wait, PBFT needs 3f+1 nodes. If n=3, 3f+1=3 => f=0. Let's just use a simple majority quorum 2 for a 3-node cluster).
        self.quorum = len(self.all_nodes) // 2 + 1 if len(self.all_nodes) > 1 else 1

        # State storage: msg_id -> dict of phases -> count
        self.prepares: Dict[str, set] = {}
        self.commits: Dict[str, set] = {}
        self.messages: Dict[str, Any] = {}
        self.committed: set = set()
        
    async def propose(self, msg_id: str, payload: Dict[str, Any]) -> bool:
        logger.info(f"Node {self.node_id} initiating PBFT for msg {msg_id}")
        self.messages[msg_id] = payload
        
        # PRE-PREPARE Phase
        req = {
            "msg_id": msg_id,
            "payload": payload,
            "primary_id": self.node_id
        }
        
        # Self vote for PRE-PREPARE -> leads to PREPARE
        await self.handle_pre_prepare(req)
        
        # Broadcast PRE-PREPARE
        tasks = []
        for peer in self.peers:
            tasks.append(rpc_client.send_message(peer, "/pbft/pre-prepare", req))
        asyncio.create_task(self._gather_and_ignore(tasks))
        
        # Wait for commit
        start_time = time.time()
        while time.time() - start_time < 5.0: # 5 sec timeout
            if msg_id in self.committed:
                return True
            await asyncio.sleep(0.1)
            
        return False

    async def handle_pre_prepare(self, req: Dict[str, Any]):
        msg_id = req["msg_id"]
        # In a real PBFT we validate signature and view number.
        # Here we just accept and move to PREPARE.
        self.messages[msg_id] = req["payload"]
        
        prep_req = {
            "msg_id": msg_id,
            "node_id": self.node_id
        }
        
        # Self vote
        await self.handle_prepare(prep_req)
        
        # Broadcast PREPARE
        tasks = []
        for peer in self.peers:
            tasks.append(rpc_client.send_message(peer, "/pbft/prepare", prep_req))
        asyncio.create_task(self._gather_and_ignore(tasks))

    async def handle_prepare(self, req: Dict[str, Any]):
        msg_id = req["msg_id"]
        node_id = req["node_id"]
        
        if msg_id not in self.prepares:
            self.prepares[msg_id] = set()
            
        self.prepares[msg_id].add(node_id)
        
        # Check if we reached quorum for PREPARE
        if len(self.prepares[msg_id]) >= self.quorum:
            # We have enough PREPAREs, broadcast COMMIT
            # Only do this once per msg_id
            if msg_id not in self.commits:
                self.commits[msg_id] = set()
                
                commit_req = {
                    "msg_id": msg_id,
                    "node_id": self.node_id
                }
                
                # Self vote
                await self.handle_commit(commit_req)
                
                tasks = []
                for peer in self.peers:
                    tasks.append(rpc_client.send_message(peer, "/pbft/commit", commit_req))
                asyncio.create_task(self._gather_and_ignore(tasks))

    async def handle_commit(self, req: Dict[str, Any]):
        msg_id = req["msg_id"]
        node_id = req["node_id"]
        
        if msg_id not in self.commits:
            self.commits[msg_id] = set()
            
        self.commits[msg_id].add(node_id)
        
        if len(self.commits[msg_id]) >= self.quorum:
            if msg_id not in self.committed:
                self.committed.add(msg_id)
                logger.info(f"Node {self.node_id} COMMITTED msg {msg_id}")
                # Actual execution is handled by the caller who checks self.committed

    async def _gather_and_ignore(self, tasks):
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

pbft_node = PBFTNode(settings.NODE_ID, settings.peer_nodes)
