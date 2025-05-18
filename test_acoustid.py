#!/usr/bin/env python
import asyncio
import os
import sys
from app.services.audio_identification.acoustid_service import AcoustIDClient, AcoustIDError

async def test_acoustid():
    # Check environment variables
    api_key = os.getenv("ACOUSTID_APP_API_KEY")
    print(f"ACOUSTID_APP_API_KEY set: {'Yes' if api_key else 'No'}")
    
    # If no API key, try to set a test key for this script only
    if not api_key:
        print("Warning: No API key found. Using a temporary test key for this script.")
        # For debugging purposes only (will use a fake test key)
        api_key = "test_key_for_debugging"
    
    # Test for fpcalc existence
    try:
        print("Testing fpcalc availability...")
        process = await asyncio.create_subprocess_exec(
            'which', 'fpcalc',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0 and stdout:
            fpcalc_path = stdout.decode().strip()
            print(f"fpcalc found at: {fpcalc_path}")
        else:
            print("fpcalc not found in PATH")
            return
    except Exception as e:
        print(f"Error checking fpcalc: {e}")
        return
    
    # Check if there are any audio files in the current directory to test with
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
    audio_files = []
    
    for root, _, files in os.walk('.', topdown=True):
        if '.git' in root or 'node_modules' in root:
            continue
        for file in files:
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(os.path.join(root, file))
        if len(audio_files) >= 5:  # Limit to 5 files
            break
    
    if not audio_files:
        print("No audio files found for testing")
        return
    
    print(f"Found {len(audio_files)} audio files for testing")
    
    # Test the AcoustID client
    try:
        # Create client with the API key we checked above
        client = AcoustIDClient(api_key=api_key)
        print("AcoustIDClient initialized successfully")
        
        # Try the first audio file
        test_file = audio_files[0]
        print(f"Testing with file: {test_file}")
        
        result = await client.lookup_fingerprint(test_file, metadata=['recordings'])
        if result:
            print("AcoustID lookup successful!")
            score = result.get('score', 'N/A')
            print(f"Score: {score}")
            
            recordings = result.get('recordings', [])
            if recordings:
                recording = recordings[0]
                print(f"Top match: '{recording.get('title', 'Unknown')}' by '{recording.get('artists', [{}])[0].get('name', 'Unknown')}'")
            else:
                print("No recordings found in the result")
        else:
            print("AcoustID lookup returned no results")
            
    except AcoustIDError as e:
        print(f"AcoustIDError: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_acoustid()) 