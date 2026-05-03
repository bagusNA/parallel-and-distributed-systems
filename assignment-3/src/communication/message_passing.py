import aiohttp
import asyncio
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class MessagePassingClient:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def stop(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_message(self, node_url: str, endpoint: str, payload: Dict[str, Any], timeout: int = 5) -> Optional[
        Dict[str, Any]]:
        if not self.session:
            await self.start()

        url = f"{node_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            async with self.session.get(url, json=payload, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            logger.warning(f"Timeout getting message to {url}")
        except aiohttp.ClientError as e:
            logger.warning(f"Error getting message to {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting message to {url}: {e}")
        return None

    async def send_message(self, node_url: str, endpoint: str, payload: Dict[str, Any], timeout: int = 5) -> Optional[Dict[str, Any]]:
        if not self.session:
            await self.start()
            
        url = f"{node_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            async with self.session.post(url, json=payload, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            logger.warning(f"Timeout sending message to {url}")
        except aiohttp.ClientError as e:
            logger.warning(f"Error sending message to {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending message to {url}: {e}")
        return None

rpc_client = MessagePassingClient()
