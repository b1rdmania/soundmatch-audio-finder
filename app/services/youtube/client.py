from typing import Dict, Any
import re
from ...core.config import settings
from ...core.logging import logger
from ...core.exceptions import InvalidURLError
import requests
import os

class YouTubeClient:
    def __init__(self):
        # Use the explicit API key provided, or try environment variable, or use settings
        self.api_key = os.environ.get("YOUTUBE_API_KEY") or "AIzaSyDnDHd2yqtnbR8-U0jFjBlTrEEQC8jY1iA"
        logger.info(f"YouTube client initialized with API key: {self.api_key[:5]}...{self.api_key[-5:]}")

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\?\/]+)',
            r'youtube\.com\/shorts\/([^&\?\/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise InvalidURLError("Invalid YouTube URL format")

    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get video information from YouTube Data API."""
        try:
            response = requests.get(
                'https://www.googleapis.com/youtube/v3/videos',
                params={
                    'part': 'snippet,contentDetails,statistics',
                    'id': video_id,
                    'key': self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                raise InvalidURLError("Video not found")
            
            video = data['items'][0]
            return {
                'id': video_id,
                'title': video['snippet']['title'],
                'channel': video['snippet']['channelTitle'],
                'duration': video['contentDetails']['duration'],
                'view_count': video['statistics'].get('viewCount'),
                'thumbnail': video['snippet']['thumbnails']['high']['url'],
                'published_at': video['snippet']['publishedAt']
            }
        except Exception as e:
            logger.error(f"Error getting YouTube video info: {str(e)}")
            raise

# Create global YouTube client instance
youtube_client = YouTubeClient() 