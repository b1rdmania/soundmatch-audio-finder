import asyncio
import json
import os
import logging
from app.services.audio_identification.acoustid_service import acoustid_client
import tempfile
import aiofiles
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_process_file():
    print("Starting test_process_file()...")
    
    # Replace with a path to an actual audio file for testing
    test_file_path = "LOVE.mp3"
    if not os.path.exists(test_file_path):
        print(f"Test file not found: {test_file_path}. Skipping example usage.")
        return

    # Read the file content
    with open(test_file_path, "rb") as f:
        content = f.read()

    # Create a temporary file
    suffix = Path(test_file_path).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        print(f"Created temporary file at: {temp_path}")
        print(f"File size: {os.path.getsize(temp_path)} bytes")
        print(f"File permissions: {oct(os.stat(temp_path).st_mode)[-3:]}")
        
        # Request recordings and release groups for metadata
        print(f"About to call AcoustID lookup with file: {temp_path}")
        acoustid_result = await acoustid_client.lookup_fingerprint(
            temp_path, 
            metadata=['recordings', 'releasegroups', 'compress']
        )
        print(f"AcoustID lookup result: {acoustid_result}")

        if acoustid_result and acoustid_result.get('score', 0) > 0.5:
            print(f"AcoustID recognized track with score: {acoustid_result['score']}")
            
            if acoustid_result.get('recordings'):
                recording = acoustid_result['recordings'][0]
                print(f"Recording details: {recording}")
                recognized_track = {
                    "title": recording.get('title'),
                    "subtitle": recording.get('artists', [{}])[0].get('name'),
                    "acoustid_id": acoustid_result.get('id'),
                    "mbid": recording.get('id'),
                    "score": acoustid_result.get('score')
                }
                print(f"Mapped AcoustID result: {recognized_track}")
            else:
                print("AcoustID result found, but no recording metadata available.")
                print(f"Available keys in result: {acoustid_result.keys()}")
                
                # Create a recognized track with just the AcoustID ID
                if acoustid_result.get('id'):
                    recognized_track = {
                        "title": f"Unknown Track (AcoustID: {acoustid_result.get('id')[:8]}...)",
                        "subtitle": "Unknown Artist",
                        "acoustid_id": acoustid_result.get('id'),
                        "score": acoustid_result.get('score')
                    }
                    print(f"Created fallback recognized track: {recognized_track}")
                else:
                    recognized_track = None
                    print("No usable data in AcoustID result")
        else:
            print(f"AcoustID did not recognize the track or score too low ({acoustid_result.get('score') if acoustid_result else 'N/A'}).")
            recognized_track = None

        print(f"Final recognized_track: {recognized_track}")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print(f"Cleaned up temporary file: {temp_path}")

if __name__ == "__main__":
    asyncio.run(test_process_file()) 