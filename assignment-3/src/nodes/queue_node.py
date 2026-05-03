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

class AckRequest(BaseModel):
    topic: str
    msg_id: str

class NackRequest(BaseModel):
    topic: str
    msg_id: str
    message: Dict[str, Any]
    retry_count: int = 0

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
        # In real systems, we move to a 'processing' set here.
        # For simplicity, we just return it.
        return {"status": "consumed", "message": msg}
    else:
        return {"status": "empty", "message": None}

@app.post("/queue/ack")
async def ack_message(req: AckRequest):
    # In a full impl, we'd remove from 'processing' set
    return {"status": "acked", "msg_id": req.msg_id}

@app.post("/queue/nack")
async def nack_message(req: NackRequest):
    if req.retry_count >= 3:
        # Move to Dead Letter Queue
        dlq_key = f"dlq:{req.topic}"
        await redis_client.rpush(dlq_key, json.dumps({
            "msg_id": req.msg_id,
            "message": req.message,
            "error": "max_retries"
        }))
        return {"status": "failed_max_retries", "msg_id": req.msg_id}
    
    # Requeue with incremented retry count
    queue_key = f"queue:{req.topic}"
    new_message = {
        "msg_id": req.msg_id,
        "payload": req.message,
        "retry_count": req.retry_count + 1
    }
    await redis_client.rpush(queue_key, json.dumps(new_message))
    return {"status": "requeued", "msg_id": req.msg_id, "retry_count": req.retry_count + 1}
