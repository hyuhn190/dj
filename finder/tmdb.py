# finder/tmdb.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def search_tv_show(query):
    url = f"{TMDB_BASE_URL}/search/tv"
    params = {"api_key": TMDB_API_KEY, "query": query}
    response = requests.get(url, params=params)
    return response.json().get("results", [])
# finder/tmdb.py
def get_tv_details(tv_id):
    url = f"{TMDB_BASE_URL}/tv/{tv_id}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    return response.json()

# finder/tmdb.py
def get_season_episodes(tv_id, season_number):
    url = f"{TMDB_BASE_URL}/tv/{tv_id}/season/{season_number}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    return response.json()

