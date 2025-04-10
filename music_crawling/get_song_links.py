import requests
from bs4 import BeautifulSoup
import time
import os

START_URLS = {
    "https://hopamchuan.com/rhythm/v/ballad": 10000,
    "https://hopamchuan.com/rhythm/v/disco": 1500,
    "https://hopamchuan.com/rhythm/v/blue": 3000,
    "https://hopamchuan.com/rhythm/v/slow": 1500
}

OUTPUT_FILE = "music_crawling/song_links.txt"

# Load existing links (optional but helpful)
existing_links = set()
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        existing_links = set(line.strip() for line in f)

def crawl_song_links(start_url, offset):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for i in range(0, offset, 10):
            next_page = f"{start_url}?offset={i}"
            print(f"Crawling: {next_page}")
            try:
                response = requests.get(next_page, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Request failed: {e}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            for a_tag in soup.find_all("a", class_="song-title"):
                href = a_tag.get("href")
                if href and href not in existing_links:
                    f.write(href + "\n")
                    print(f"Saved: {href}")
                    existing_links.add(href)
            time.sleep(1)

if __name__ == "__main__":
    for START_URL, offset in START_URLS.items():
        crawl_song_links(START_URL, offset)
