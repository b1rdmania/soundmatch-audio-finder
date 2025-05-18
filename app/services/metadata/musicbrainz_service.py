import asyncio
import httpx
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MUSICBRAINZ_API_URL = "https://musicbrainz.org/ws/2"
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"

class MusicBrainzClient:
    """Client for interacting with the MusicBrainz API."""

    def __init__(self):
        self.base_url = MUSICBRAINZ_API_URL
        self.headers = {
            "User-Agent": "SoundMatch/1.0.0 (https://github.com/yourusername/soundmatch)",
            "Accept": "application/json"
        }
        logger.info(f"MusicBrainzClient initialized with SSL verification: {VERIFY_SSL}")

    async def search_recording(self, query: str) -> Dict[str, Any]:
        """Search for a recording in MusicBrainz."""
        try:
            async with httpx.AsyncClient(verify=VERIFY_SSL) as client:
                params = {
                    "query": query,
                    "fmt": "json"
                }
                response = await client.get(
                    f"{self.base_url}/recording",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.SSLError as e:
            logger.error(f"SSL verification failed: {e}")
            if VERIFY_SSL:
                logger.info("Consider setting VERIFY_SSL=false if using a self-signed certificate")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching MusicBrainz: {e}")
            raise

    # ... rest of the file stays the same ... 