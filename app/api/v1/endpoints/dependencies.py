from fastapi import Depends
from app.services.metadata.musixmatch import musixmatch_service, MusixmatchService
from app.services.metadata.jamendo import jamendo_service, JamendoService
from app.services.ai.gemini_service import gemini_service, GeminiService
from app.services.metadata.musicbrainz import musicbrainz_client, MusicBrainzClient
from app.services.metadata.discogs_service import discogs_service, DiscogsService
from app.services.metadata.wikipedia_service import wikipedia_service, WikipediaService
from app.services.audio_identification.acoustid_service import acoustid_client, AcoustIDClient

# Simple dependency injections that return service instances
def get_musixmatch_service():
    return musixmatch_service

def get_jamendo_service():
    return jamendo_service

def get_gemini_service():
    return gemini_service

def get_musicbrainz_service():
    return musicbrainz_client

def get_discogs_service():
    return discogs_service

def get_wikipedia_service():
    return wikipedia_service

def get_acoustid_client() -> AcoustIDClient:
    """Get AcoustID client instance."""
    from app.services.audio_identification.acoustid_service import acoustid_client, AcoustIDClient
    import os
    
    # Check if API key is set
    api_key = os.getenv("ACOUSTID_APP_API_KEY")
    if not api_key:
        # Handle missing API key - raise clear exception
        raise ValueError("ACOUSTID_APP_API_KEY environment variable not set. AcoustID features are disabled.")
    
    # Create client if it doesn't exist (for deployment environment)
    if acoustid_client is None:
        try:
            return AcoustIDClient()
        except Exception as e:
            # Log the error and re-raise with more context
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize AcoustIDClient: {e}")
            raise ValueError(f"Failed to initialize AcoustIDClient. Original error: {e}")
            
    return acoustid_client 