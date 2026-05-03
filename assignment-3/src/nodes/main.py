from src.nodes.base_node import app
from src.utils.config import settings

if settings.NODE_TYPE == "lock_manager":
    import src.nodes.lock_manager
elif settings.NODE_TYPE == "queue_node":
    import src.nodes.queue_node
elif settings.NODE_TYPE == "cache_node":
    import src.nodes.cache_node
