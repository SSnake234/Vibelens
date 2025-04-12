import os
import json
from pinecone import Pinecone
import time
from pinecone import PineconeApiException
from dotenv import load_dotenv

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_host = os.getenv("PINECONE_HOST")

pc = Pinecone(
    api_key=pinecone_api_key,
)
index = pc.Index(host = pinecone_host)

metadata_path = "music_crawling\song_metadata"
records = []

for filename in os.listdir(metadata_path):
    if not filename.endswith(".json"):
        continue

    with open(os.path.join(metadata_path, filename), "r", encoding="utf-8") as f:
        data = json.load(f)

    content = f"{data['title']} by {data['artist']}. Genre: {data['genre']}.\nLyrics:\n{data['lyrics']}"

    record = {
        "_id": f"{data['id']}",
        "text": content,
        "category": data["genre"]
    }

    records.append(record)

batch_size = 96
for i in range(0, len(records), batch_size):
    batch = records[i:i + batch_size]
    try:
        index.upsert_records("", batch)
        print(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")
    except PineconeApiException as e:
        print(f"Error in batch {i // batch_size + 1}: {e}")
        print("⏳ Waiting 60 seconds before retrying...")
        time.sleep(60)
        try:
            index.upsert_records("", batch)
            print(f"Retried and upserted batch {i // batch_size + 1}")
        except PineconeApiException as e2:
            print(f"Failed again on retry: {e2}")
