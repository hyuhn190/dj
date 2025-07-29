# finder/views.py
from django.shortcuts import render
from .tmdb import search_tv_show

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
