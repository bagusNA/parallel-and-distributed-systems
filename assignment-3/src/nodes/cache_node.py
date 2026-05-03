import time
import asyncio
from typing import Any, Dict, Optional
from collections import OrderedDict
from pydantic import BaseModel
from fastapi import HTTPException

from src.nodes.base_node import app
from src.utils.config import settings
from src.communication.message_passing import rpc_client

class CacheEntry:
    def __init__(self, value: Any, state: str, version: int):
        self.value = value
        self.state = state  # 'M', 'E', 'S', 'I'
        self.version = version
        self.last_accessed = time.time()

class LRUCache:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str) -> Optional[CacheEntry]:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key].last_accessed = time.time()
            return self.cache[key]
        return None

    def put(self, key: str, value: Any, state: str, version: int):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = CacheEntry(value, state, version)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def invalidate(self, key: str):
        if key in self.cache:
            self.cache[key].state = 'I'
            
local_cache = LRUCache()
peers = [p for p in settings.peer_nodes if p != f"http://{settings.NODE_ID}:{settings.PORT}"]

class WriteRequest(BaseModel):
    value: Any
    version: int

class MESIReadRequest(BaseModel):
    key: str

class MESIInvalidateRequest(BaseModel):
    key: str

@app.get("/cache/{key}")
async def read_cache(key: str):
    if settings.NODE_TYPE != "cache_node":
        raise HTTPException(status_code=400, detail="Not a cache node")

    entry = local_cache.get(key)
    
    # If local is valid, return it
    if entry and entry.state in ['M', 'E', 'S']:
        return {"key": key, "value": entry.value, "state": entry.state, "version": entry.version}
        
    # Local is Invalid or missing, fetch from peers
    tasks = []
    for peer in peers:
        tasks.append(rpc_client.send_message(peer, "/mesi/read", {"key": key}))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    best_entry = None
    for result in results:
        if isinstance(result, dict) and result.get("found"):
            if best_entry is None or result["version"] > best_entry["version"]:
                best_entry = result
                
    if best_entry:
        # We got it from a peer, state becomes 'S'
        local_cache.put(key, best_entry["value"], 'S', best_entry["version"])
        return {"key": key, "value": best_entry["value"], "state": 'S', "version": best_entry["version"]}
        
    raise HTTPException(status_code=404, detail="Key not found in cache cluster")

@app.post("/cache/{key}")
async def write_cache(key: str, req: WriteRequest):
    if settings.NODE_TYPE != "cache_node":
        raise HTTPException(status_code=400, detail="Not a cache node")

    # Write locally and set state to 'M'
    local_cache.put(key, req.value, 'M', req.version)
    
    # Broadcast invalidate to all peers
    tasks = []
    for peer in peers:
        tasks.append(rpc_client.send_message(peer, "/mesi/invalidate", {"key": key}))
    # Fire and forget invalidations (or wait, but in real life we wait for ACKs)
    await asyncio.gather(*tasks, return_exceptions=True)
    
    return {"status": "written", "key": key, "state": "M"}

# MESI Peer Endpoints
@app.post("/mesi/read")
async def mesi_read(req: MESIReadRequest):
    if settings.NODE_TYPE != "cache_node":
        return {"found": False}
        
    entry = local_cache.get(req.key)
    if entry and entry.state in ['M', 'E', 'S']:
        # If we had M or E, we must downgrade to S because another node is reading it
        if entry.state in ['M', 'E']:
            entry.state = 'S'
            
        return {
            "found": True,
            "value": entry.value,
            "state": entry.state,
            "version": entry.version
        }
    return {"found": False}

@app.post("/mesi/invalidate")
async def mesi_invalidate(req: MESIInvalidateRequest):
    if settings.NODE_TYPE != "cache_node":
        return {"status": "ignored"}
    local_cache.invalidate(req.key)
    return {"status": "invalidated"}
