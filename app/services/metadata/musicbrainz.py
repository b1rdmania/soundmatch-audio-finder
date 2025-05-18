import requests
from typing import Dict, Any, Optional, List
from ...core.logging import logger
from ...core.exceptions import MetadataAPIError
import asyncio
import musicbrainzngs # Keep the library import

class MusicBrainzClient:
    """Client for interacting with MusicBrainz API."""
    
    # BASE_URL = "https://musicbrainz.org/ws/2" # Not needed for library
    USER_AGENT = "SoundMatch/1.0 (andy@example.com)" # Replace with actual contact if possible
    
    def __init__(self):
        # Setup musicbrainzngs user agent
        try:
            musicbrainzngs.set_useragent(app="SoundMatch", version="1.0", contact="andy@example.com") # Replace with actual contact
        except Exception as e:
            logger.error(f"Failed to set MusicBrainz user agent: {e}")
            # Decide if this is critical or can proceed without it

    async def _search_recordings_async(self, title: str, artist: str, limit: int = 5):
        """Internal async wrapper for musicbrainzngs search."""
        try:
            # Use to_thread as musicbrainzngs is synchronous
            logger.debug(f"Querying MusicBrainz with: recording:\"{title}\" AND artist:\"{artist}\"")
            result = await asyncio.to_thread(
                musicbrainzngs.search_recordings,
                query=f'recording:"{title}" AND artist:"{artist}"', 
                limit=limit,
                strict=True 
            )
            return result
        except (musicbrainzngs.UsageError, musicbrainzngs.ResponseError) as exc:
            logger.error(f"MusicBrainz usage or response parsing error: {exc}", exc_info=True)
            logger.error(f"This often indicates an issue with the data received from MusicBrainz or how it's being parsed (e.g., unexpected attributes like 'type-id' in aliases).")
            # Potentially log the raw query or parts of the response if safe and useful
            # For now, just returning None as per existing logic
            return None
        except musicbrainzngs.WebServiceError as exc:
            logger.error(f"MusicBrainz API WebServiceError during recording search: {exc}", exc_info=True)
            # This could be network issues, authentication, rate limiting, etc.
            return None
        except Exception as e:
            logger.error(f"Unexpected error during MusicBrainz search: {e}", exc_info=True)
            return None

    async def get_musicbrainz_data(self, title: str, artist: str) -> Optional[Dict[str, Any]]:
        """Search MusicBrainz for a recording and return useful metadata like tags and MBID."""
        logger.info(f"Searching MusicBrainz for data for: '{title}' by '{artist}'")
        
        results = await self._search_recordings_async(title=title, artist=artist)
        
        if not results:
            logger.warning(f"MusicBrainz search call failed or returned empty for: '{title}' by '{artist}'")
            return None

        recordings = results.get('recording-list', [])
        if not recordings:
            logger.warning(f"MusicBrainz found no recordings for: '{title}' by '{artist}'")
            return None

        # Select the best match (often the first one with high score)
        best_match = recordings[0]
        score = int(best_match.get('ext:score', '0'))
        mbid = best_match.get('id')

        if score < 80 or not mbid: # Lowered threshold slightly, ensure MBID exists
            logger.warning(f"MusicBrainz top match score ({score}) too low or no MBID for: '{title}'. Skipping.")
            return None
        
        logger.info(f"Found potential MusicBrainz match (MBID: {mbid}, Score: {score}) for '{title}'")

        # Extract relevant data from the best match
        mb_data = {"mbid": mbid, "match_score": score}
        
        # Get tags if available
        tags = best_match.get('tag-list', [])
        if tags:
            mb_data["tags"] = [tag['name'] for tag in tags if 'name' in tag]
            logger.info(f"Extracted MusicBrainz tags: {mb_data['tags']}")

        # We could potentially fetch more data using the MBID here if needed (e.g., genres)
        # using musicbrainzngs.get_recording_by_id(mbid, includes=["genres"]) 
        # but keep it simple for now.

        return mb_data
            
    # --- Remove old/unused methods --- 
    # async def search_track(self, query: str) -> Optional[Dict[str, Any]]: ...
    # def _extract_mood(self, tags: list) -> str: ...
    # def get_track_features(self, track_name: str, artist_name: str) -> Dict[str, Any]: ...
    # def _extract_features(self, tags: list, ratings: list, genres: list) -> Dict[str, Any]: ...

# Create a global instance
musicbrainz_client = MusicBrainzClient() 