import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict, Any

from src.communication.message_passing import rpc_client
from src.utils.config import settings
from src.consensus.raft import raft_node

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting Node: {settings.NODE_ID} (Type: {settings.NODE_TYPE})")
    await rpc_client.start()
    if settings.NODE_TYPE == "lock_manager":
        await raft_node.start()
    yield
    # Shutdown
    logger.info(f"Stopping Node: {settings.NODE_ID}")
    if settings.NODE_TYPE == "lock_manager":
        await raft_node.stop()
    await rpc_client.stop()

app = FastAPI(title=f"Node {settings.NODE_ID}", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok", "node_id": settings.NODE_ID, "node_type": settings.NODE_TYPE}

class RequestVotePayload(BaseModel):
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int

class AppendEntriesPayload(BaseModel):
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[Dict[str, Any]]
    leader_commit: int

@app.post("/raft/request_vote")
async def request_vote(payload: RequestVotePayload):
    if settings.NODE_TYPE != "lock_manager":
        return {"term": 0, "vote_granted": False}
    return raft_node.handle_request_vote(
        payload.term, payload.candidate_id, payload.last_log_index, payload.last_log_term
    )

@app.post("/raft/append_entries")
async def append_entries(payload: AppendEntriesPayload):
    if settings.NODE_TYPE != "lock_manager":
        return {"term": 0, "success": False}
    return raft_node.handle_append_entries(
        payload.term, payload.leader_id, payload.prev_log_index, payload.prev_log_term, payload.entries, payload.leader_commit
    )

from src.consensus.pbft import pbft_node

@app.post("/pbft/pre-prepare")
async def pbft_pre_prepare(payload: Dict[str, Any]):
    if settings.NODE_TYPE == "queue_node":
        await pbft_node.handle_pre_prepare(payload)
    return {"status": "ok"}

@app.post("/pbft/prepare")
async def pbft_prepare(payload: Dict[str, Any]):
    if settings.NODE_TYPE == "queue_node":
        await pbft_node.handle_prepare(payload)
    return {"status": "ok"}

@app.post("/pbft/commit")
async def pbft_commit(payload: Dict[str, Any]):
    if settings.NODE_TYPE == "queue_node":
        await pbft_node.handle_commit(payload)
    return {"status": "ok"}

