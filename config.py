import requests
from qbittorrentapi import Client
import time
import os
import dotenv
from rapidfuzz import fuzz

dotenv.load_dotenv()

JACKETT_API_URL = os.getenv("JACKETT_API_URL")
JACKETT_API_KEY = os.getenv("JACKETT_API_KEY")
QBITORRENT_URL = os.getenv("QBITTORRENT_URL")
QBITTORENT_CREDS = {
    "username":"admin",
    "password":"adminadmin"
}

DOWNLOAD_DIR = "/home/ubuntu/Downloads"


def search_jackett(query, categories=[3000, 3010]):
    try:
        params = {
            "apikey": JACKETT_API_KEY,
            "Query": query,
            "Category[]": categories 
        }
        
        response = requests.get(JACKETT_API_URL, params=params)
        response.raise_for_status()

        results = response.json()
        return results.get('Results',[])
    except Exception as e:
        print(f"SeaRch Failed: {str(e)}")
        return []
    


def download_torrent(magnet):
    try:
        qbit_client = Client(
            host=QBITORRENT_URL,
            **QBITTORENT_CREDS
        )

        result = qbit_client.torrent_add(
            urls=[magnet],
            save_path=DOWNLOAD_DIR
        )

        print(f"Started download : {magnet}")
        return True
    except Exception as e:
        print(f"Download failed: {str(e)}")
        return False
    

def execute(query):
    results = search_jackett(query)
    for result in results:
        title = result.get("Title", "").lower()
        size_mb = result.get("Size", 0) / (1024 * 1024)
        magnet = result.get("MagnetUri")

        similarity = fuzz.partial_ratio(query.lower(), title)

        if (
            result.get("CategoryDesc") == "Audio" and
            size_mb < 10 and
            magnet and
            similarity > 70  # Tune this threshold (0-100)
        ):
            print(f"Found match: {title} (Score: {similarity})")
            download_torrent(magnet)
            return True

    print("No suitable MP3 match found.")
    return False

