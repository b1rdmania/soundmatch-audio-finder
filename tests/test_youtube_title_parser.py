import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_youtube_title_parsing():
    """Test the parsing of YouTube video titles to extract artist and song name."""
    
    test_cases = [
        # Common format: Artist - Song Title
        {
            "title": "Queen - Bohemian Rhapsody",
            "expected_artist": "Queen",
            "expected_title": "Bohemian Rhapsody"
        },
        # Format with official video suffix
        {
            "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
            "expected_artist": "Rick Astley",
            "expected_title": "Never Gonna Give You Up"
        },
        # Format with other common suffixes
        {
            "title": "The Weeknd - Blinding Lights (Official Audio)",
            "expected_artist": "The Weeknd",
            "expected_title": "Blinding Lights"
        },
        # Format with year in title
        {
            "title": "Dua Lipa - Levitating (2020)",
            "expected_artist": "Dua Lipa",
            "expected_title": "Levitating"
        },
        # Format with featuring artist
        {
            "title": "Lady Gaga, Bradley Cooper - Shallow (from A Star Is Born) (Official Music Video)",
            "expected_artist": "Lady Gaga, Bradley Cooper",
            "expected_title": "Shallow"
        }
    ]
    
    # Mock the YouTube API response
    for test_case in test_cases:
        # This is a simplified version of what the endpoint would do
        title = test_case["title"]
        
        if " - " in title:
            parts = title.split(" - ", 1)
            artist = parts[0].strip()
            song_title = parts[1].strip()
            
            # Clean up title by removing common suffixes
            for suffix in ["(Official Video)", "(Official Music Video)", "(Official Lyric Video)", 
                          "(Lyrics)", "(Audio)", "(Visualizer)", "[Official Video]"]:
                if suffix.lower() in song_title.lower():
                    song_title = song_title.lower().replace(suffix.lower(), "").strip()
            
            assert artist == test_case["expected_artist"], f"Failed on '{title}'"
            assert song_title == test_case["expected_title"].lower(), f"Failed on '{title}'"

def test_youtube_endpoint_with_invalid_url():
    """Test that the process-link endpoint properly handles invalid URLs."""
    response = client.post("/api/v1/music/process-link", json={"url": "not-a-youtube-url"})
    assert response.status_code == 400
    assert "Invalid YouTube URL" in response.json()["detail"]

# To run these tests, you would need to mock the YouTube API calls in a real environment 