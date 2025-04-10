import requests
from bs4 import BeautifulSoup
import time
import os
import json

song_links_path = "music_crawling/song_links.txt"
save_path = "music_crawling/song_metadata"

with open(song_links_path, "r", encoding="utf-8") as f:
    song_links = [line.strip() for line in f if line.strip()]

def clean_lyrics(lyrics):
    lyrics = lyrics.replace("\n", " ").replace("  ", " ")
    return lyrics

for idx, song_link in enumerate(song_links):
    try:
        response = requests.get(song_link, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed for {song_link}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    title_el = soup.find(id="song-title")
    artist_el = soup.find(class_="author-item")
    lyrics_el = soup.find_all(class_="hopamchuan_lyric")
    rhythm_el = soup.find(id="display-rhythm")

    if not title_el or not artist_el or not lyrics_el:
        print(f"Missing data on page: {song_link}")
        continue

    title = title_el.get_text(strip=True)
    artist = artist_el.get_text(strip=True)
    lyrics = "\n".join([el.get_text(strip=True) for el in lyrics_el])
    lyrics = clean_lyrics(lyrics)
    rhythm = rhythm_el.get_text(strip=True) if rhythm_el else "Unknown"

    # Build metadata
    song_data = {
        "id": f"song_{idx:05}",  # e.g., song_00001
        "title": title,
        "artist": artist,
        "genre": rhythm,
        "lyrics": lyrics
    }

    # Save to JSON
    safe_filename = f"{idx:05}_{title.replace(' ', '_').replace('/', '_')}.json"
    filepath = os.path.join(save_path, safe_filename)

    with open(filepath, "w", encoding="utf-8") as out_file:
        json.dump(song_data, out_file, ensure_ascii=False, indent=2)

    print(f"Saved: {song_data['id']} - {title}")
