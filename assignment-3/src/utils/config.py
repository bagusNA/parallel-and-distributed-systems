import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NODE_ID: str = os.getenv("NODE_ID", "node_1")
    NODE_TYPE: str = os.getenv("NODE_TYPE", "lock_manager")
    # Comma separated list of cluster nodes e.g. "http://node_1:8000,http://node_2:8000"
    CLUSTER_NODES: str = os.getenv("CLUSTER_NODES", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    PORT: int = int(os.getenv("PORT", "8000"))

    @property
    def peer_nodes(self) -> list[str]:
        nodes = [n.strip() for n in self.CLUSTER_NODES.split(",") if n.strip()]
        # Typically we might filter ourselves out, but we need full list for config
        return nodes

settings = Settings()
