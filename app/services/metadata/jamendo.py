from typing import Dict, List, Optional, Any
import requests
from ...core.config import settings
from ...core.logging import logger
import asyncio

class JamendoService:
    """Service for interacting with Jamendo API to find similar tracks."""
    
    BASE_URL = "https://api.jamendo.com/v3.0"
    CLIENT_ID = "b553314a"
    
    def __init__(self):
        # self.api_key = settings.JAMENDO_API_KEY # API key not typically needed for public search
        self.base_url = "https://api.jamendo.com/v3.0"
    
    @staticmethod
    def _map_spotify_mood(valence: float, energy: float) -> str:
        """Map Spotify's valence and energy values to Jamendo mood tags."""
        if valence >= 0.6 and energy >= 0.6:
            return "happy"
        elif valence <= 0.4 and energy <= 0.4:
            return "sad"
        elif energy >= 0.7:
            return "energetic"
        elif valence <= 0.3:
            return "melancholic"
        else:
            return "calm"
    
    @staticmethod
    def _is_instrumental(instrumentalness: float, danceability: float) -> bool:
        """Determine if track is likely instrumental based on Spotify features."""
        return instrumentalness > 0.5 and danceability < 0.5
    
    async def find_similar_tracks_by_keywords(
        self,
        keywords: List[str],
        limit: int = 10 # How many results to return
    ) -> List[Dict[str, Any]]:
        """
        Find similar tracks on Jamendo based on a list of keywords (tags).
        
        Args:
            keywords: List of keywords generated by AI or other means.
            limit: Max number of tracks to return.
            
        Returns:
            List of similar tracks with metadata.
        """
        if not keywords:
            logger.warning("No keywords provided for Jamendo search.")
            return []

        try:
            search_tags_str = " ".join(keywords)
            logger.info(f"Searching Jamendo with keywords: {search_tags_str}")
            
            response = await asyncio.to_thread( # Use async request
                requests.get,
                f"{self.base_url}/tracks/",
                params={
                    "client_id": self.CLIENT_ID, # Use the public CLIENT_ID
                    "format": "json",
                    "limit": limit,
                    "fuzzytags": search_tags_str,
                    "include": "musicinfo stats",
                    "boost": "popularity_total",
                    "orderby": "relevance",
                    "audioformat": "mp32",
                    "audio": 1 # Ensure tracks have audio
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Process and format results
            similar_tracks = []
            for track in data.get("results", []):
                # Add basic track info
                similar_tracks.append({
                    "id": track["id"],
                    "title": track["name"],
                    "artist": track["artist_name"],
                    "duration": str(track["duration"]),
                    "audio_url": track.get("audio", ""),
                    "download_url": track.get("audiodownload", ""),
                    "image_url": track.get("image", ""),
                    "license": track.get("license_ccurl", "Unknown License"),
                    "tags": track.get("musicinfo", {}).get("tags", {}).get("genres", []) + \
                            track.get("musicinfo", {}).get("tags", {}).get("instruments", []) + \
                            track.get("musicinfo", {}).get("tags", {}).get("vartags", []),
                    # No simple similarity score based just on keywords, could be added later
                })
            
            logger.info(f"Found {len(similar_tracks)} tracks on Jamendo for keywords: {search_tags_str}")
            return similar_tracks
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Jamendo API request failed: {str(e)}")
            return [] # Return empty list on API error
        except Exception as e:
            logger.exception(f"Error finding similar tracks on Jamendo: {str(e)}")
            return [] # Return empty list on other errors

# Create a global instance
jamendo_service = JamendoService() 