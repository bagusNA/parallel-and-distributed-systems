import pytest
from src.nodes.cache_node import LRUCache, CacheEntry

def test_cache_read_invalid_to_shared():
    cache = LRUCache()
    # Initially key is not present (Invalid)
    # Simulator read miss
    cache.put("item_1", "value_1", 'S', 1)
    entry = cache.get("item_1")
    assert entry.state == 'S'

def test_cache_write_shared_to_modified():
    cache = LRUCache()
    # Start as Shared
    cache.put("item_1", "old_val", 'S', 1)
    # Local write sets to Modified
    cache.put("item_1", "new_val", 'M', 2)
    entry = cache.get("item_1")
    assert entry.state == 'M'
    assert entry.value == "new_val"

def test_cache_external_write_to_invalid():
    cache = LRUCache()
    # Start as Shared
    cache.put("item_1", "val", 'S', 1)
    # External invalidate
    cache.invalidate("item_1")
    entry = cache.get("item_1")
    assert entry.state == 'I'

def test_cache_eviction_lru():
    cache = LRUCache(capacity=2)
    cache.put("k1", "v1", 'S', 1)
    cache.put("k2", "v2", 'S', 1)
    cache.put("k3", "v3", 'S', 1) # Should evict k1
    
    assert cache.get("k1") is None
    assert cache.get("k2") is not None
    assert cache.get("k3") is not None
