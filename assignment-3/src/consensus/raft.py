import asyncio
import logging
import time
import random
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.utils.config import settings
from src.communication.message_passing import rpc_client

logger = logging.getLogger(__name__)

class LogEntry(BaseModel):
    term: int
    command: Dict[str, Any]

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = [p for p in peers if p != f"http://{node_id}:{settings.PORT}"]
        
        # Persistent state
        self.current_term = 0
        self.voted_for = None
        self.log: List[LogEntry] = []
        
        # Volatile state
        self.commit_index = 0
        self.last_applied = 0
        
        # Volatile state on leaders
        self.next_index = {peer: 1 for peer in self.peers}
        self.match_index = {peer: 0 for peer in self.peers}
        
        # Node state
        self.state = "FOLLOWER"  # FOLLOWER, CANDIDATE, LEADER
        self.leader_id: Optional[str] = None
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(1.5, 3.0)  # Random timeout to prevent split votes
        self.heartbeat_interval = 0.5
        
        self.running = False

    async def start(self):
        self.running = True
        asyncio.create_task(self.run_election_timer())

    async def stop(self):
        self.running = False

    async def run_election_timer(self):
        while self.running:
            await asyncio.sleep(0.1)
            if self.state != "LEADER" and (time.time() - self.last_heartbeat) > self.election_timeout:
                await self.start_election()

    async def start_election(self):
        self.state = "CANDIDATE"
        self.current_term += 1
        self.voted_for = self.node_id
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(1.5, 3.0)
        
        logger.info(f"Node {self.node_id} starting election for term {self.current_term}")
        
        votes = 1
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1].term if self.log else 0
        
        payload = {
            "term": self.current_term,
            "candidate_id": self.node_id,
            "last_log_index": last_log_index,
            "last_log_term": last_log_term
        }
        
        tasks = []
        for peer in self.peers:
            tasks.append(rpc_client.send_message(peer, "/raft/request_vote", payload, timeout=1))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict) and result.get("vote_granted"):
                votes += 1
                
        if votes > (len(self.peers) + 1) / 2 and self.state == "CANDIDATE":
            logger.info(f"Node {self.node_id} became LEADER for term {self.current_term}")
            self.state = "LEADER"
            self.leader_id = self.node_id
            for peer in self.peers:
                self.next_index[peer] = len(self.log) + 1
                self.match_index[peer] = 0
            asyncio.create_task(self.send_heartbeats())
        else:
            self.state = "FOLLOWER"

    async def send_heartbeats(self):
        while self.running and self.state == "LEADER":
            tasks = []
            for peer in self.peers:
                prev_log_index = self.next_index[peer] - 1
                prev_log_term = self.log[prev_log_index - 1].term if prev_log_index > 0 else 0
                entries = [e.dict() for e in self.log[prev_log_index:]]
                
                payload = {
                    "term": self.current_term,
                    "leader_id": self.node_id,
                    "prev_log_index": prev_log_index,
                    "prev_log_term": prev_log_term,
                    "entries": entries,
                    "leader_commit": self.commit_index
                }
                tasks.append(self.send_append_entries(peer, payload))
                
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(self.heartbeat_interval)

    async def send_append_entries(self, peer, payload):
        result = await rpc_client.send_message(peer, "/raft/append_entries", payload, timeout=1)
        if result and isinstance(result, dict):
            if result.get("term", 0) > self.current_term:
                self.current_term = result["term"]
                self.state = "FOLLOWER"
                self.voted_for = None
            elif result.get("success"):
                self.next_index[peer] = payload["prev_log_index"] + len(payload["entries"]) + 1
                self.match_index[peer] = self.next_index[peer] - 1
                self.update_commit_index()
            else:
                self.next_index[peer] = max(1, self.next_index[peer] - 1)

    def update_commit_index(self):
        for n in range(len(self.log), self.commit_index, -1):
            if self.log[n-1].term == self.current_term:
                match_count = 1
                for peer in self.peers:
                    if self.match_index[peer] >= n:
                        match_count += 1
                if match_count > (len(self.peers) + 1) / 2:
                    self.commit_index = n
                    break

    def handle_request_vote(self, term: int, candidate_id: str, last_log_index: int, last_log_term: int):
        if term > self.current_term:
            self.current_term = term
            self.state = "FOLLOWER"
            self.voted_for = None
            
        if term < self.current_term:
            return {"term": self.current_term, "vote_granted": False}
            
        my_last_log_index = len(self.log) - 1
        my_last_log_term = self.log[-1].term if self.log else 0
        
        log_ok = (last_log_term > my_last_log_term) or (last_log_term == my_last_log_term and last_log_index >= my_last_log_index)
        
        if (self.voted_for is None or self.voted_for == candidate_id) and log_ok:
            self.voted_for = candidate_id
            self.last_heartbeat = time.time()
            return {"term": self.current_term, "vote_granted": True}
            
        return {"term": self.current_term, "vote_granted": False}

    def handle_append_entries(self, term: int, leader_id: str, prev_log_index: int, prev_log_term: int, entries: List[Dict], leader_commit: int):
        if term > self.current_term:
            self.current_term = term
            self.state = "FOLLOWER"
            self.voted_for = None
            
        if term < self.current_term:
            return {"term": self.current_term, "success": False}
            
        self.last_heartbeat = time.time()
        self.leader_id = leader_id
        
        if prev_log_index > len(self.log):
            return {"term": self.current_term, "success": False}
            
        if prev_log_index > 0 and self.log[prev_log_index - 1].term != prev_log_term:
            self.log = self.log[:prev_log_index - 1]
            return {"term": self.current_term, "success": False}
            
        # Append any new entries not already in the log
        for i, entry in enumerate(entries):
            log_idx = prev_log_index + i
            if log_idx < len(self.log):
                if self.log[log_idx].term != entry['term']:
                    self.log = self.log[:log_idx]
                    self.log.append(LogEntry(**entry))
            else:
                self.log.append(LogEntry(**entry))
                
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log))
            
        return {"term": self.current_term, "success": True}

    async def propose(self, command: Dict[str, Any]):
        if self.state != "LEADER":
            return False, self.leader_id
            
        entry = LogEntry(term=self.current_term, command=command)
        self.log.append(entry)
        index = len(self.log)
        
        # Wait for commit
        start_time = time.time()
        while time.time() - start_time < 2.0:  # 2s timeout
            if self.commit_index >= index:
                return True, self.node_id
            await asyncio.sleep(0.05)
            
        return False, self.node_id

raft_node = RaftNode(settings.NODE_ID, settings.peer_nodes)
