# finder/views.py
from django.shortcuts import render
from requests import Response
from django.http import HttpResponse
from .tmdb import search_tv_show
import pysrt  # pip install pysrt
from .subtitles import search_subtitles, download_subtitle_file, select_best_subtitle
import os


def index(request):
    query = request.GET.get("query")
    results = search_tv_show(query) if query else []
    return render(request, "index.html", {"results": results, "query": query})


# finder/views.py
from .tmdb import search_tv_show, get_tv_details


def show_seasons(request, tv_id):
    tv_info = get_tv_details(tv_id)
    seasons = tv_info.get("seasons", [])
    return render(request, "seasons.html", {
        "tv_id": tv_id,
        "tv_name": tv_info.get("name", ""),
        "seasons": seasons,
    })


# finder/views.py
from .tmdb import get_season_episodes


def show_episodes(request, tv_id, season_number):
    season_data = get_season_episodes(tv_id, season_number)
    episodes = season_data.get("episodes", [])
    tv_name = season_data.get("name", "未知剧集")
    return render(request, "episodes.html", {
        "tv_id": tv_id,
        "season_number": season_number,
        "tv_name": tv_name,
        "episodes": episodes,
    })




def episode_detail(request, tv_id, season_number, episode_number):
    tv_info = get_tv_details(tv_id)
    tv_name = tv_info.get("name", "未知剧集")
    save_directory = os.path.join("subtitles", f"{tv_name}_S{season_number:02d}")
    file_name = f"S{season_number:02d}E{episode_number:02d}.srt"
    print(f"正在处理 {tv_name} 第{season_number}季 第{episode_number}集的字幕...")
    file_path = os.path.join(save_directory, file_name)

    # 检查本地是否有字幕文件
    if not os.path.exists(file_path):
        # 没有则搜索并下载整季字幕
        from .subtitles import download_season_subtitles_single
        os.makedirs(save_directory, exist_ok=True)
        download_season_subtitles_single(tv_name, season_number, save_directory)

    # 读取字幕内容
    subtitles = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            subtitles = f.readlines()

    return render(request, "subtitle.html", {
        "tv_name": tv_name,
        "season_number": season_number,
        "episode_number": episode_number,
        "subtitles": subtitles,
    })
