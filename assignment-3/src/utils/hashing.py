import hashlib
import bisect
from typing import List

class ConsistentHashing:
    def __init__(self, nodes: List[str], virtual_nodes: int = 100):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        for node in nodes:
            self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node: str):
        for i in range(self.virtual_nodes):
            v_node_key = f"{node}:{i}"
            h = self._hash(v_node_key)
            self.ring[h] = node
            bisect.insort(self.sorted_keys, h)

    def remove_node(self, node: str):
        for i in range(self.virtual_nodes):
            v_node_key = f"{node}:{i}"
            h = self._hash(v_node_key)
            if h in self.ring:
                del self.ring[h]
                self.sorted_keys.remove(h)

    def get_node(self, key: str) -> str:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
