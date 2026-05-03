import uuid
from pydantic import BaseModel
from fastapi import HTTPException
import redis.asyncio as redis
from src.nodes.base_node import app
from src.utils.config import settings
from src.consensus.raft import raft_node

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class LockRequest(BaseModel):
    resource_id: str
    lock_type: str = "exclusive"
    owner_id: str
    timeout: int = 5000

class LockRelease(BaseModel):
    resource_id: str
    owner_id: str

@app.post("/lock/acquire")
async def acquire_lock(req: LockRequest):
    if settings.NODE_TYPE == "lock_manager":
        success, leader_id = await raft_node.propose({
            "action": "acquire",
            "resource_id": req.resource_id,
            "owner_id": req.owner_id,
            "timeout": req.timeout
        })
        if not success:
            raise HTTPException(status_code=307, detail=f"Redirect to leader: {leader_id}")
            
    # Fallback to Redis for simple lock if Raft is not fully integrated or just Phase 1 
    lock_key = f"lock:{req.resource_id}"
    acquired = await redis_client.set(lock_key, req.owner_id, nx=True, px=req.timeout)
    
    if acquired:
        return {"status": "acquired", "resource_id": req.resource_id, "owner_id": req.owner_id}
    else:
        raise HTTPException(status_code=409, detail="Lock already acquired")

@app.post("/lock/release")
async def release_lock(req: LockRelease):
    if settings.NODE_TYPE == "lock_manager":
        success, leader_id = await raft_node.propose({
            "action": "release",
            "resource_id": req.resource_id,
            "owner_id": req.owner_id
        })
        if not success:
            raise HTTPException(status_code=307, detail=f"Redirect to leader: {leader_id}")

    lock_key = f"lock:{req.resource_id}"
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    result = await redis_client.eval(script, 1, lock_key, req.owner_id)
    if result:
        return {"status": "released", "resource_id": req.resource_id}
    else:
        raise HTTPException(status_code=400, detail="Not lock owner or lock does not exist")

