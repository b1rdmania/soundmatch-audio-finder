import os
import mutagen
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3

def extract_id3_tags(file_path):
    """Extract ID3 tags from an MP3 file and print them in a readable format."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"Analyzing file: {file_path}")
    print(f"File size: {os.path.getsize(file_path)} bytes")
    
    try:
        # First try using ID3 directly
        audio = ID3(file_path)
        print("\nID3 tags found:")
        for key in audio:
            if key.startswith('APIC'):
                print(f"{key}: [Image data]")
            else:
                print(f"{key}: {audio[key]}")
        
    except ID3NoHeaderError:
        print("No ID3 header found, trying MP3...")
        
    # Try also with MP3 class
    try:
        audio = MP3(file_path)
        print("\nMP3 info:")
        print(f"Length: {audio.info.length:.2f} seconds")
        print(f"Bitrate: {audio.info.bitrate/1000:.0f} kbps")
        print(f"Sample rate: {audio.info.sample_rate} Hz")
        print(f"Channels: {audio.info.channels}")
        
        # Try alternative tag formats if present
        if hasattr(audio, 'tags') and audio.tags:
            print("\nTags found:")
            for key in audio.tags:
                print(f"{key}: {audio.tags[key]}")
    
    except Exception as e:
        print(f"Error reading MP3 file: {e}")
    
    # Try with generic mutagen
    try:
        audio = mutagen.File(file_path)
        if audio:
            print("\nGeneric tag info:")
            for key, value in audio.items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error with generic mutagen: {e}")

if __name__ == "__main__":
    file_path = "LOVE.mp3"  # The file to analyze
    extract_id3_tags(file_path) 