import os
import json
from mutagen import File
from pathlib import Path

def generate_manifest(songs_directory):
    """
    Scan the songs directory and generate a manifest.json file containing
    information about all MP3 files and their associated cover images.
    """
    manifest = []
    songs_path = Path(songs_directory)

    # Walk through all subdirectories in the Songs folder
    for folder_path in [x for x in songs_path.iterdir() if x.is_dir()]:
        # Find MP3 and image files in the folder
        mp3_files = list(folder_path.glob("*.mp3"))
        image_files = list(folder_path.glob("*.jpg")) + list(folder_path.glob("*.png"))
        
        if not mp3_files:
            print(f"Warning: No MP3 file found in {folder_path}")
            continue
            
        if not image_files:
            print(f"Warning: No cover image found in {folder_path}")
            continue

        # Process the first MP3 file in the folder
        mp3_path = mp3_files[0]
        cover_path = image_files[0]
        
        try:
            # Read metadata from MP3
            audio = File(mp3_path)
            
            # Extract title and artist, using filename as fallback
            title = None
            artist = None
            
            if hasattr(audio, 'tags'):
                # ID3 tags (MP3)
                if audio.tags:
                    title = str(audio.tags.get('TIT2', mp3_path.stem))
                    artist = str(audio.tags.get('TPE1', 'Unknown Artist'))
            else:
                # Other formats
                title = audio.get('title', [mp3_path.stem])[0]
                artist = audio.get('artist', ['Unknown Artist'])[0]
            
            # Use filename if no metadata found
            if not title:
                title = mp3_path.stem
            if not artist:
                artist = 'Unknown Artist'

            # Create relative paths for web use
            relative_audio_path = "Songs\\"+str(mp3_path.relative_to(songs_path))
            relative_cover_path = "Songs\\"+str(cover_path.relative_to(songs_path))
            
            # Add to manifest
            song_info = {
                "title": title,
                "artist": artist,
                "audioPath": relative_audio_path.replace('\\', '/'),
                "coverPath": relative_cover_path.replace('\\', '/')
            }
            
            manifest.append(song_info)
            print(f"Added: {title} by {artist}")
            
        except Exception as e:
            print(f"Error processing {mp3_path}: {str(e)}")
    
    # Sort manifest by title
    manifest.sort(key=lambda x: x['title'])
    
    # Write manifest file
    manifest_path = songs_path / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nManifest generated with {len(manifest)} songs")
    print(f"Manifest saved to: {manifest_path}")

if __name__ == "__main__":
    # Get the script's directory
    script_dir = Path(__file__).parent
    
    # Look for Songs directory in the same folder as the script
    songs_dir = script_dir / "Songs"
    
    if not songs_dir.exists():
        print("Error: 'Songs' directory not found!")
        print(f"Please create a 'Songs' directory at: {songs_dir}")
        exit(1)
    
    generate_manifest(songs_dir)