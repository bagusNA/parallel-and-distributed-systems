import uuid
import json
from typing import Any, Dict
from pydantic import BaseModel
from fastapi import HTTPException
import redis.asyncio as redis

from src.nodes.base_node import app
from src.utils.config import settings
from src.consensus.pbft import pbft_node
from src.utils.hashing import ConsistentHashing
from src.communication.message_passing import rpc_client

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
ring = ConsistentHashing(settings.peer_nodes)

class PublishRequest(BaseModel):
    topic: str
    message: Dict[str, Any]

class ConsumeRequest(BaseModel):
    consumer_id: str
    topic: str

@app.post("/queue/publish")
async def publish_message(req: PublishRequest):
    if settings.NODE_TYPE != "queue_node":
        raise HTTPException(status_code=400, detail="Not a queue node")
        
    target_node_url = ring.get_node(req.topic)
    my_url = f"http://{settings.NODE_ID}:{settings.PORT}"
    
    # If we are not the target node, forward the request
    if target_node_url and target_node_url != my_url:
        result = await rpc_client.send_message(target_node_url, "/queue/publish", req.dict())
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to forward to partition owner")

    # We are the owner for this topic. Initiate PBFT consensus.
    msg_id = str(uuid.uuid4())
    payload = {
        "topic": req.topic,
        "message": req.message
    }
    
    success = await pbft_node.propose(msg_id, payload)
    
    if success:
        # Consensus reached. Push to Redis queue.
        queue_key = f"queue:{req.topic}"
        await redis_client.rpush(queue_key, json.dumps({"msg_id": msg_id, "payload": req.message}))
        return {"status": "published", "msg_id": msg_id, "topic": req.topic}
    else:
        raise HTTPException(status_code=500, detail="Consensus failed")

@app.post("/queue/consume")
async def consume_message(req: ConsumeRequest):
    if settings.NODE_TYPE != "queue_node":
        raise HTTPException(status_code=400, detail="Not a queue node")

    target_node_url = ring.get_node(req.topic)
    my_url = f"http://{settings.NODE_ID}:{settings.PORT}"
    
    if target_node_url and target_node_url != my_url:
        result = await rpc_client.send_message(target_node_url, "/queue/consume", req.dict())
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to forward to partition owner")

    queue_key = f"queue:{req.topic}"
    msg_str = await redis_client.lpop(queue_key)
    if msg_str:
        msg = json.loads(msg_str)
        return {"status": "consumed", "message": msg}
    else:
        return {"status": "empty", "message": None}
