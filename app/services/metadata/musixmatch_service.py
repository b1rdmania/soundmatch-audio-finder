import asyncio
import httpx
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MUSIXMATCH_API_URL = "https://api.musixmatch.com/ws/1.1"
MUSIXMATCH_API_KEY = os.getenv("MUSIXMATCH_API_KEY")

class MusixmatchClient:
    """Client for interacting with the Musixmatch API."""

    def __init__(self):
        if not MUSIXMATCH_API_KEY:
            raise ValueError("MUSIXMATCH_API_KEY environment variable must be set")
        
        self.base_url = MUSIXMATCH_API_URL
        self.api_key = MUSIXMATCH_API_KEY
        logger.info("MusixmatchClient initialized successfully")

    async def search_track(self, query: str) -> Dict[str, Any]:
        """Search for a track in Musixmatch."""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q_track": query,
                    "apikey": self.api_key,
                    "format": "json"
                }
                response = await client.get(
                    f"{self.base_url}/track.search",
                    params=params
                )
                
                if response.status_code == 401:
                    logger.error("Invalid Musixmatch API key")
                    raise ValueError("Invalid Musixmatch API key. Please check your MUSIXMATCH_API_KEY environment variable.")
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching Musixmatch: {e}")
            raise

    # ... rest of the file stays the same ... 