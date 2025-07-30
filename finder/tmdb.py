# finder/tmdb.py
import os
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


# 创建带重试策略的会话
def create_session():
    session = requests.Session()

    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=retry_strategy
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# 全局会话实例
api_session = create_session()


def search_tv_show(query):
    url = f"{TMDB_BASE_URL}/search/tv"
    params = {"api_key": TMDB_API_KEY, "query": query}
    response = api_session.get(url, params=params)
    return response.json().get("results", [])


def get_tv_details(tv_id):
    url = f"{TMDB_BASE_URL}/tv/{tv_id}"
    params = {"api_key": TMDB_API_KEY}
    response = api_session.get(url, params=params)
    return response.json()


def get_season_episodes(tv_id, season_number):
    url = f"{TMDB_BASE_URL}/tv/{tv_id}/season/{season_number}"
    params = {"api_key": TMDB_API_KEY}
    response = api_session.get(url, params=params)
    return response.json()
