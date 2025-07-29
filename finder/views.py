# finder/views.py
from django.shortcuts import render
from .tmdb import search_tv_show

def index(request):
    query = request.GET.get("query")
    results = search_tv_show(query) if query else []
    return render(request, "index.html", {"results": results, "query": query})
