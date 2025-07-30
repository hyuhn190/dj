# finder/views.py
from django.shortcuts import render, Http404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from .services.show_service import ShowService
from .services.subtitle_service import SubtitleService
from .services.translate_service import TranslateService
from .services.tts_service import TTSService
from .providers.tts.windows_sapi import WindowsSAPIBackend
from .task import download_subtitles_task, generate_tts_task
# 初始化服务实例
show_service = ShowService()
subtitle_service = SubtitleService()
translate_service = TranslateService()
tts_service = TTSService(WindowsSAPIBackend())


def index(request):
    """
    首页视图，处理美剧搜索请求
    """
    query = request.GET.get('query', '').strip()
    results = []
    if query:
        results = show_service.search_tv(query)
    return render(request, 'index.html', {
        'query': query,
        'results': results,
    })


def show_seasons(request, tv_id):
    """
    显示指定美剧的所有季信息
    """
    tv_info = show_service.get_tv(tv_id)
    if not tv_info:
        raise Http404("美剧不存在")

    seasons = show_service.get_seasons(tv_id)
    return render(request, 'seasons.html', {
        'tv_id': tv_id,
        'tv_name': tv_info['name'],
        'seasons': seasons,
    })


def show_episodes(request, tv_id, season_number):
    """
    显示指定季的所有集信息
    """
    tv_info = show_service.get_tv(tv_id)
    if not tv_info:
        raise Http404("美剧不存在")

    episodes = show_service.get_episodes(tv_id, season_number)
    return render(request, 'episodes.html', {
        'tv_id': tv_id,
        'tv_name': tv_info['name'],
        'season_number': season_number,
        'episodes': episodes,
    })


def episode_detail(request, tv_id, season_number, episode_number):
    """
    显示指定集的字幕详情
    """
    tv_info = show_service.get_tv(tv_id)
    if not tv_info:
        raise Http404("美剧不存在")

    # 获取字幕并解析
    subtitle_result = subtitle_service.get_episode_viewdata(tv_id, season_number, episode_number)

    return render(request, 'subtitle.html', {
        'tv_id': tv_id,
        'tv_name': subtitle_result['tv_name'],
        'season_number': season_number,
        'episode_number': episode_number,
        'segments': subtitle_result['segments'],
    })


# === API 接口 ===

@require_GET
def translate_word(request):
    """
    翻译单词 API
    GET /api/translate?word=hello
    """
    word = request.GET.get("word", "").strip()
    if not word:
        return HttpResponseBadRequest("missing word")

    try:
        result = translate_service.translate(word)
        # 根据结果中是否有错误信息确定状态码
        status = 200 if "error" not in result else 502
        return JsonResponse(result, status=status)
    except Exception as e:
        return JsonResponse({"word": word, "error": f"{type(e).__name__}: {e}"}, status=502)


@require_GET
def tts_word(request):
    word = request.GET.get("word", "").strip()
    if not word:
        return HttpResponseBadRequest("missing word")

    # 尝试从缓存获取
    tts_service = TTSService(WindowsSAPIBackend())
    result = tts_service.ensure_word_wav(word)

    if "url" in result:
        status = 200
    else:
        # 如果文件不存在，触发异步生成
        generate_tts_task.delay(word)
        # 立即返回处理中状态
        result = {"word": word, "status": "processing", "message": "TTS generation started"}
        status = 202  # Accepted

    return JsonResponse(result, status=status)