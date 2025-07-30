# Table of Contents
- .env
- db.sqlite3
- manage.py
- finder\admin.py
- finder\apps.py
- finder\models.py
- finder\subtitles.py
- finder\subtitle_parser.py
- finder\task.py
- finder\tests.py
- finder\tmdb.py
- finder\urls.py
- finder\views.py
- finder\__init__.py
- finder\migrations\__init__.py
- finder\providers\__init__.py
- finder\providers\tts\windows_sapi.py
- finder\providers\tts\__init__.py
- finder\repo\subtitle_repo.py
- finder\repo\tts_repo.py
- finder\repo\__init__.py
- finder\services\parse_service.py
- finder\services\show_service.py
- finder\services\subtitle_service.py
- finder\services\translate_service.py
- finder\services\tts_service.py
- finder\services\__init__.py
- subtitle_project\asgi.py
- subtitle_project\celery.py
- subtitle_project\settings.py
- subtitle_project\urls.py
- subtitle_project\wsgi.py
- subtitle_project\__init__.py
- templates\episodes.html
- templates\index.html
- templates\seasons.html
- templates\subtitle.html

## File: .env

- Extension: 
- Language: unknown
- Size: 104 bytes
- Created: 2025-07-29 23:12:32
- Modified: 2025-07-29 23:37:38

### Code

```unknown
TMDB_API_KEY = "f7169d1bb681f77b0773658a676d8a4a"
OPENSUB_API_KEY= "DQ0O7m6MVqAtQXvcJ7c6CdCunFwmnIIV"

```

## File: db.sqlite3

- Extension: .sqlite3
- Language: unknown
- Size: 0 bytes
- Created: 2025-07-29 23:15:57
- Modified: 2025-07-29 23:15:57

### Code

```unknown

```

## File: manage.py

- Extension: .py
- Language: python
- Size: 694 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-29 23:10:14

### Code

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitle_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

```

## File: finder\admin.py

- Extension: .py
- Language: python
- Size: 66 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-29 23:10:16

### Code

```python
from django.contrib import admin

# Register your models here.

```

## File: finder\apps.py

- Extension: .py
- Language: python
- Size: 150 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-29 23:10:16

### Code

```python
from django.apps import AppConfig


class FinderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finder"

```

## File: finder\models.py

- Extension: .py
- Language: python
- Size: 60 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-29 23:10:16

### Code

```python
from django.db import models

# Create your models here.

```

## File: finder\subtitles.py

- Extension: .py
- Language: python
- Size: 4940 bytes
- Created: 2025-07-29 23:38:08
- Modified: 2025-07-31 00:04:24

### Code

```python
# finder/subtitles.py
import requests
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = "DQ0O7m6MVqAtQXvcJ7c6CdCunFwmnIIV"
APP_NAME = "testapi"
APP_VERSION = "1"


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


def search_subtitles(query="Breaking Bad", season=1, episode=None):
    # 使用正确的OpenSubtitles API端点
    url = "https://api.opensubtitles.com/api/v1/subtitles"

    # 设置请求头
    headers = {
        "Api-Key": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": f"{APP_NAME} v{APP_VERSION}"
    }

    # 设置查询参数
    params = {
        'query': query,
        'season_number': season,
        'languages': 'en'  # 只搜索英文字幕
    }

    # 如果指定了集数，则添加集数参数
    if episode:
        params['episode_number'] = episode

    try:
        resp = api_session.get(url, headers=headers, params=params)

        # 检查响应
        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError as e:
                print("Failed to decode JSON:", e)
                return None
        else:
            print(f"API Error: {resp.status_code} - {resp.text}")
            return None

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def download_subtitle_file(file_id, file_name, save_directory):
    """
    下载单个字幕文件
    """
    # 创建下载链接
    url = "https://api.opensubtitles.com/api/v1/download"

    headers = {
        "Api-Key": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": f"{APP_NAME} v{APP_VERSION}"
    }

    # 请求下载链接
    data = {
        "file_id": file_id
    }

    try:
        resp = api_session.post(url, headers=headers, json=data)

        if resp.status_code == 200:
            download_info = resp.json()
            download_link = download_info.get('link')

            if download_link:
                # 下载字幕文件
                subtitle_resp = api_session.get(download_link)

                if subtitle_resp.status_code == 200:
                    # 确保保存目录存在
                    os.makedirs(save_directory, exist_ok=True)

                    # 保存文件
                    file_path = os.path.join(save_directory, file_name)
                    with open(file_path, 'wb') as f:
                        f.write(subtitle_resp.content)
                    print(f"已下载字幕文件: {file_name}")
                    return True
                else:
                    print(f"下载字幕文件失败: {subtitle_resp.status_code}")
            else:
                print("无法获取下载链接")
        else:
            print(f"获取下载链接失败: {resp.status_code} - {resp.text}")

    except requests.RequestException as e:
        print(f"下载请求失败: {e}")

    return False

# 其余函数保持不变...

def select_best_subtitle(subtitles_list):
    """
    从字幕列表中选择最佳字幕
    选择规则:
    1. 优先选择下载次数多的
    2. 优先选择评分高的
    3. 优先选择非听力障碍专用的
    4. 优先选择高清字幕
    """
    if not subtitles_list:
        return None

    # 按优先级排序
    def sort_key(subtitle):
        attr = subtitle['attributes']
        # 下载次数权重最高，然后是评分，避免听力障碍专用，优先高清
        return (
            -attr['download_count'],  # 负号表示降序
            -attr['ratings'],
            attr['hearing_impaired'],  # False(0)排在True(1)前面
            -attr['hd']  # True(1)排在False(0)前面
        )

    # 按规则排序并返回最佳字幕
    sorted_subtitles = sorted(subtitles_list, key=sort_key)
    return sorted_subtitles[0]

def download_season_subtitles_single(show_name, season, save_directory):
    """
    为每集下载一个最佳英文字幕文件
    """
    print(f"正在下载 {show_name} 第{season}季的英文字幕...")

    # 搜索整季字幕
    results = search_subtitles(query=show_name, season=season)

    if not results or not results['data']:
        print("未找到相关字幕")
        return


```

## File: finder\subtitle_parser.py

- Extension: .py
- Language: python
- Size: 1491 bytes
- Created: 2025-07-30 22:05:39
- Modified: 2025-07-30 23:54:46

### Code

```python
# finder/subtitle_parser.py
import re
import pysrt

WORD_RE = re.compile(r"[A-Za-z]+'[A-Za-z]+|[A-Za-z]+")

def parse_srt_to_segments(file_path: str):
    """
    读取 .srt ，按条目解析，返回：
    [
      { "index": 1, "start": "00:00:01,000", "end": "00:00:02,000",
        "text": "Hello world!", "words": ["Hello","world"] },
      ...
    ]
    """
    subs = pysrt.open(file_path, encoding='utf-8', error_handling='ignore')
    segments = []
    for item in subs:
        # 去掉简单的斜体标签；复杂 HTML 可再做清洗
        text = (item.text or "").replace("<i>", "").replace("</i>", "")
        words = WORD_RE.findall(text)
        segments.append({
            "index": item.index,
            "start": str(item.start),
            "end": str(item.end),
            "text": text,
            "words": words,
        })
    return segments

def parse_srt_generator(file_path: str):
    """
    生成器版本的字幕解析，节省内存
    """
    subs = pysrt.open(file_path, encoding='utf-8', error_handling='ignore')
    for item in subs:
        # 去掉简单的斜体标签；复杂 HTML 可再做清洗
        text = (item.text or "").replace("<i>", "").replace("</i>", "")
        words = WORD_RE.findall(text)
        yield {
            "index": item.index,
            "start": str(item.start),
            "end": str(item.end),
            "text": text,
            "words": words,
        }

```

## File: finder\task.py

- Extension: .py
- Language: python
- Size: 951 bytes
- Created: 2025-07-30 23:51:46
- Modified: 2025-07-31 00:01:20

### Code

```python
# finder/tasks.py
from celery import shared_task
from .subtitles import download_subtitle_file
from .services.tts_service import TTSService
from .providers.tts.windows_sapi import WindowsSAPIBackend

@shared_task
def download_subtitles_task(show_name, season, save_directory):
    """
    异步下载字幕任务
    """
    try:
        download_subtitle_file(show_name, season, save_directory)
        return {"status": "success", "message": f"Downloaded subtitles for {show_name} Season {season}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@shared_task
def generate_tts_task(word):
    """
    异步生成TTS音频任务
    """
    try:
        tts_service = TTSService(WindowsSAPIBackend())
        result = tts_service.ensure_word_wav(word)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

```

## File: finder\tests.py

- Extension: .py
- Language: python
- Size: 828 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-30 22:41:00

### Code

```python
# finder/tests.py
from django.test import TestCase
from .services.parse_service import ParseService
import tempfile, textwrap, os

class ParseServiceTests(TestCase):
    def test_parse_srt_basic(self):
        content = textwrap.dedent("""\
        1
        00:00:01,000 --> 00:00:02,000
        Hello world!

        2
        00:00:03,000 --> 00:00:04,000
        It's fine.
        """)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "S01E01.srt")
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            svc = ParseService()
            segs = svc.parse_srt(p)
            self.assertEqual(len(segs), 2)
            self.assertEqual(segs[0]["words"], ["Hello","world"])
            self.assertIn("It's", segs[1]["words"])

```

## File: finder\tmdb.py

- Extension: .py
- Language: python
- Size: 1471 bytes
- Created: 2025-07-29 23:13:51
- Modified: 2025-07-30 23:54:46

### Code

```python
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

```

## File: finder\urls.py

- Extension: .py
- Language: python
- Size: 615 bytes
- Created: 2025-07-29 23:11:27
- Modified: 2025-07-30 23:21:58

### Code

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('show/<int:tv_id>/', views.show_seasons, name='show_seasons'),
    path('show/<int:tv_id>/season/<int:season_number>/', views.show_episodes, name='show_episodes'),
    path('show/<int:tv_id>/season/<int:season_number>/episode/<int:episode_number>/', views.episode_detail, name='episode_detail'),

    # 新增 API
    path('api/translate', views.translate_word, name='api_translate'),  # GET ?word=
    path('api/tts', views.tts_word, name='api_tts'),                    # GET ?word=
]

```

## File: finder\views.py

- Extension: .py
- Language: python
- Size: 3800 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-30 23:54:46

### Code

```python
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
```

## File: finder\__init__.py

- Extension: .py
- Language: python
- Size: 0 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-29 23:10:16

### Code

```python

```

## File: finder\migrations\__init__.py

- Extension: .py
- Language: python
- Size: 0 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-29 23:10:16

### Code

```python

```

## File: finder\providers\__init__.py

- Extension: .py
- Language: python
- Size: 0 bytes
- Created: 2025-07-30 22:53:19
- Modified: 2025-07-30 22:53:19

### Code

```python

```

## File: finder\providers\tts\windows_sapi.py

- Extension: .py
- Language: python
- Size: 781 bytes
- Created: 2025-07-30 22:53:37
- Modified: 2025-07-30 22:53:42

### Code

```python
# finder/providers/tts/windows_sapi.py
class WindowsSAPIBackend:
    """
    仅负责“把文本合成为指定路径的 WAV”，不关心路径/URL/缓存。
    """
    def synthesize_to_file(self, text: str, wav_path: str) -> None:
        import win32com.client
        try:
            from win32com.client import constants
            open_mode = getattr(constants, "SSFMCreateForWrite", 3)
        except Exception:
            open_mode = 3  # 兜底

        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        stream.Open(wav_path, open_mode)
        speaker.AudioOutputStream = stream
        speaker.Speak(text)
        stream.Close()
        speaker.AudioOutputStream = None

```

## File: finder\providers\tts\__init__.py

- Extension: .py
- Language: python
- Size: 0 bytes
- Created: 2025-07-30 22:53:29
- Modified: 2025-07-30 22:53:29

### Code

```python

```

## File: finder\repo\subtitle_repo.py

- Extension: .py
- Language: python
- Size: 1244 bytes
- Created: 2025-07-30 22:38:08
- Modified: 2025-07-30 22:38:14

### Code

```python
# finder/repos/subtitle_repo.py
import os
from django.conf import settings

class SubtitleRepo:
    """
    负责字幕文件的路径策略与读写（不关心业务规则）。
    """
    def season_dir(self, show_name: str, season: int) -> str:
        # 统一保存目录：media/subtitles/<剧名>_Sxx/
        return os.path.join(settings.MEDIA_ROOT, "subtitles", f"{show_name}_S{season:02d}")

    def episode_file_name(self, season: int, episode: int) -> str:
        # 命名规则：SxxExx.srt（与你现有命名保持一致）
        return f"S{season:02d}E{episode:02d}.srt"

    def episode_path(self, show_name: str, season: int, episode: int) -> str:
        return os.path.join(self.season_dir(show_name, season), self.episode_file_name(season, episode))

    def ensure_season_dir(self, show_name: str, season: int) -> str:
        d = self.season_dir(show_name, season)
        os.makedirs(d, exist_ok=True)
        return d

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def save_bytes(self, path: str, content: bytes) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)

```

## File: finder\repo\tts_repo.py

- Extension: .py
- Language: python
- Size: 705 bytes
- Created: 2025-07-30 22:38:26
- Modified: 2025-07-30 22:38:32

### Code

```python
# finder/repos/tts_repo.py
import os
from django.conf import settings

class TTSRepo:
    def dir(self) -> str:
        return os.path.join(settings.MEDIA_ROOT, "tts")

    def wav_path_for_word(self, word: str) -> str:
        safe = "".join([c for c in word if c.isalnum() or c in ("_", "-", "'")]).strip("'") or "tts"
        return os.path.join(self.dir(), f"{safe.lower()}.wav")

    def url_for(self, path: str) -> str:
        return f"{settings.MEDIA_URL}tts/{os.path.basename(path)}"

    def ensure_dir(self) -> str:
        d = self.dir()
        os.makedirs(d, exist_ok=True)
        return d

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

```

## File: finder\repo\__init__.py

- Extension: .py
- Language: python
- Size: 0 bytes
- Created: 2025-07-30 22:40:37
- Modified: 2025-07-30 22:40:37

### Code

```python

```

## File: finder\services\parse_service.py

- Extension: .py
- Language: python
- Size: 293 bytes
- Created: 2025-07-30 22:38:50
- Modified: 2025-07-30 22:41:00

### Code

```python
# finder/services/parse_service.py
from ..subtitle_parser import parse_srt_to_segments

class ParseService:
    """
    对解析器做一层轻封装，便于将来替换或预处理。
    """
    def parse_srt(self, file_path: str):
        return parse_srt_to_segments(file_path)

```

## File: finder\services\show_service.py

- Extension: .py
- Language: python
- Size: 1917 bytes
- Created: 2025-07-30 22:59:19
- Modified: 2025-07-30 23:18:04

### Code

```python
# finder/services/show_service.py
from ..tmdb import get_tv_details  # 直接复用你现有的 TMDB 封装
from ..services.parse_service import ParseService
from ..services.subtitle_service import SubtitleService
from ..tmdb import search_tv_show, get_tv_details, get_season_episodes

class ShowService:
    """
    聚合服务：围绕“某一集字幕页面”所需数据做编排。
    """
    def __init__(self, subtitle_svc: SubtitleService | None = None, parse_svc: ParseService | None = None):
        self.subtitle_svc = subtitle_svc or SubtitleService()
        self.parse_svc = parse_svc or ParseService()

    def get_episode_viewdata(self, tv_id: int, season: int, episode: int) -> dict:
        tv_info = get_tv_details(tv_id)  # 你当前就是这么拿剧名/季集信息的
        tv_name = tv_info.get("name", "未知剧集")

        srt_path = self.subtitle_svc.ensure_episode_file(tv_name, season, episode)
        segments = self.parse_svc.parse_srt(srt_path) if srt_path else []

        return {
            "tv_name": tv_name,
            "season_number": season,
            "episode_number": episode,
            "segments": segments,
        }

    def search_tv(self, query):
        """
        搜索电视剧
        """
        return search_tv_show(query)

    def get_tv(self, tv_id):
        """
        获取电视剧详情
        """
        return get_tv_details(tv_id)

    def get_seasons(self, tv_id):
        """
        获取电视剧的所有季信息
        """
        tv_info = self.get_tv(tv_id)
        return tv_info.get("seasons", []) if tv_info else []

    def get_episodes(self, tv_id, season_number):
        """
        获取指定季的所有集信息
        """
        season_data = get_season_episodes(tv_id, season_number)
        return season_data.get("episodes", []) if season_data else []
```

## File: finder\services\subtitle_service.py

- Extension: .py
- Language: python
- Size: 1868 bytes
- Created: 2025-07-30 22:59:03
- Modified: 2025-07-31 00:03:07

### Code

```python
# finder/services/subtitle_service.py
from ..repo.subtitle_repo import SubtitleRepo
from django.conf import settings
from ..subtitles import download_season_subtitles_single  # 复用现有实现
from ..tmdb import get_tv_details  # 获取电视剧详情
from ..services.parse_service import ParseService

class SubtitleService:
    """
    负责确保某一集的字幕在本地可用（若无则触发整季下载），并返回该集的 .srt 路径。
    行为与现状保持一致。
    """
    def __init__(self, repo: SubtitleRepo | None = None, parse_svc: ParseService | None = None):
        self.repo = repo or SubtitleRepo()
        self.parse_svc = parse_svc or ParseService()

    def ensure_episode_file(self, show_name: str, season: int, episode: int) -> str | None:
        season_dir = self.repo.ensure_season_dir(show_name, season)
        file_path = self.repo.episode_path(show_name, season, episode)

        # 若已存在，直接返回
        if self.repo.exists(file_path):
            return file_path

        # 若不存在：触发整季下载（与当前 episode_detail 的行为一致）
        download_season_subtitles_single(show_name, season, season_dir)

        # 下载完成后再检查一次
        return file_path if self.repo.exists(file_path) else None

    def get_episode_viewdata(self, tv_id: int, season: int, episode: int) -> dict:
        tv_info = get_tv_details(tv_id)  # 获取剧名/季集信息
        tv_name = tv_info.get("name", "未知剧集")

        srt_path = self.ensure_episode_file(tv_name, season, episode)
        segments = self.parse_svc.parse_srt(srt_path) if srt_path else []

        return {
            "tv_name": tv_name,
            "season_number": season,
            "episode_number": episode,
            "segments": segments,
        }

```

## File: finder\services\translate_service.py

- Extension: .py
- Language: python
- Size: 4384 bytes
- Created: 2025-07-30 22:52:56
- Modified: 2025-07-30 23:54:46

### Code

```python
# finder/services/translate_service.py
import time, random
from django.core.cache import cache
from django.conf import settings

# deep-translator 兜底（如果可用）
try:
    from deep_translator import GoogleTranslator as DTGoogle
    _USE_DEEP = True
except Exception:
    _USE_DEEP = False

from googletrans import Translator

DEFAULT_SERVICE_URLS = getattr(settings, "GOOGLETRANS_SERVICE_URLS", [
    "translate.google.com",
    "translate.google.com.hk",
    "translate.googleapis.com",
])
REQUEST_TIMEOUT = int(getattr(settings, "GOOGLETRANS_TIMEOUT", 5))
CACHE_TTL = int(getattr(settings, "TRANSLATE_CACHE_TTL", 60 * 60))  # 1h

def _make_translator(urls):
    t = Translator(service_urls=urls, raise_exception=True)
    # 兼容属性名差异（与你当前视图实现保持一致）
    if not hasattr(t, 'raise_exception'):
        setattr(t, 'raise_exception', True)
    if not hasattr(t, 'raise_Exception'):
        setattr(t, 'raise_Exception', True)
    return t

class TranslateService:
    """
    负责将"多域名轮换 + 重试 + 兜底 + 缓存"封装为一个可复用的服务。
    """

    def __init__(self, service_urls=None, cache_prefix="trans:"):
        self.service_urls = list(service_urls or DEFAULT_SERVICE_URLS)
        self.cache_prefix = cache_prefix
        # 预加载高频词汇
        self._preload_common_words()

    def _preload_common_words(self):
        """
        预加载高频词汇到缓存
        """
        common_words = ['hello', 'world', 'good', 'morning', 'thank you', 'please', 'yes', 'no']
        for word in common_words:
            cache_key = f"{self.cache_prefix}en:zh-cn:{word.lower()}"
            if not cache.get(cache_key):
                try:
                    # 异步预加载，避免阻塞
                    self.translate(word)
                except:
                    pass  # 忽略预加载错误

    def _translate_with_failover(self, word, src='en', dest='zh-cn', max_total_attempts=6):
        urls_round = self.service_urls.copy()
        random.shuffle(urls_round)
        last_err = None
        attempts = 0
        for base in urls_round:
            tr = _make_translator([base])
            for _ in range(2):  # 每个域名尝试 2 次（与你当前实现一致）
                attempts += 1
                if attempts > max_total_attempts:
                    break
                try:
                    res = tr.translate(word, src=src, dest=dest)  # requests 超时由底层控制
                    return res.text
                except Exception as e:
                    last_err = e
                    time.sleep(0.2)
            if attempts > max_total_attempts:
                break
        if last_err:
            raise last_err
        raise RuntimeError("translation failed with no specific error")

    def translate(self, word: str, src='en', dest='zh-cn') -> dict:
        # 使用更细粒度的缓存键
        cache_key = f"{self.cache_prefix}{src}:{dest}:{word.lower()}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # 先试 googletrans + 域名轮换
        try:
            text = self._translate_with_failover(word, src=src, dest=dest, max_total_attempts=6)
            data = {"word": word, "src": src, "dest": dest, "text": text, "engine": "googletrans"}
            # 根据词长度设置不同的过期时间
            expire_time = 7*24*60*60 if len(word) < 5 else 24*60*60
            cache.set(cache_key, data, expire_time)
            return data
        except Exception as e_gt:
            # 兜底 deep-translator（与当前实现一致）
            if _USE_DEEP:
                try:
                    text = DTGoogle(source=src, target=dest).translate(word)
                    data = {"word": word, "src": src, "dest": dest, "text": text, "engine": "deep-translator"}
                    expire_time = 7*24*60*60 if len(word) < 5 else 24*60*60
                    cache.set(cache_key, data, expire_time)
                    return data
                except Exception:
                    pass
            # 两者都失败，返回错误信息（视图将据此设置 502）
            return {"word": word, "error": f"{type(e_gt).__name__}: {e_gt}"}

```

## File: finder\services\tts_service.py

- Extension: .py
- Language: python
- Size: 938 bytes
- Created: 2025-07-30 22:53:51
- Modified: 2025-07-30 22:54:14

### Code

```python
# finder/services/tts_service.py
import os
from django.conf import settings
from ..repo.tts_repo import TTSRepo

class TTSService:
    """
    负责：安全文件名 → 是否已存在 → 需要则调用后端生成 → 返回可访问 URL。
    """
    def __init__(self, backend, repo: TTSRepo | None = None):
        self.backend = backend
        self.repo = repo or TTSRepo()

    def ensure_word_wav(self, word: str) -> dict:
        safe = "".join([c for c in word if c.isalnum() or c in ("_", "-", "'")]).strip("'") or "tts"
        path = self.repo.wav_path_for_word(safe)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            try:
                self.backend.synthesize_to_file(word, path)
            except Exception as e:
                return {"error": f"TTS failed: {type(e).__name__}: {e}"}
        return {"url": self.repo.url_for(path)}

```

## File: finder\services\__init__.py

- Extension: .py
- Language: python
- Size: 0 bytes
- Created: 2025-07-30 22:40:24
- Modified: 2025-07-30 22:40:24

### Code

```python

```

## File: subtitle_project\asgi.py

- Extension: .py
- Language: python
- Size: 425 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-29 23:10:14

### Code

```python
"""
ASGI config for subtitle_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitle_project.settings")

application = get_asgi_application()

```

## File: subtitle_project\celery.py

- Extension: .py
- Language: python
- Size: 369 bytes
- Created: 2025-07-30 23:51:27
- Modified: 2025-07-30 23:54:46

### Code

```python
# subtitle_project/celery.py
import os
from celery import Celery

# 设置Django的设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subtitle_project.settings')

app = Celery('subtitle_project')

# 使用Django设置中的配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

```

## File: subtitle_project\settings.py

- Extension: .py
- Language: python
- Size: 4156 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-31 00:10:37

### Code

```python
"""
Django settings for subtitle_project project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-!mr1ja6qaq=8p1mmdws#)#ln&chgx&i_cc261v#m7-2awqy(pm"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'finder.apps.FinderConfig',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "subtitle_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "subtitle_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# 静态模板配置（确保加上）
import os
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'templates')]


from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# 追加：
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# 在subtitle_project/settings.py末尾添加
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# Celery 配置
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

```

## File: subtitle_project\urls.py

- Extension: .py
- Language: python
- Size: 354 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-30 22:11:00

### Code

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('finder.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

```

## File: subtitle_project\wsgi.py

- Extension: .py
- Language: python
- Size: 425 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-29 23:10:14

### Code

```python
"""
WSGI config for subtitle_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitle_project.settings")

application = get_wsgi_application()

```

## File: subtitle_project\__init__.py

- Extension: .py
- Language: python
- Size: 100 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-30 23:54:46

### Code

```python
# subtitle_project/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)

```

## File: templates\episodes.html

- Extension: .html
- Language: html
- Size: 587 bytes
- Created: 2025-07-29 23:34:08
- Modified: 2025-07-29 23:39:45

### Code

```html
<!-- templates/episodes.html -->
<!DOCTYPE html>
<html>
<head><title>{{ tv_name }} - 第 {{ season_number }} 季</title></head>
<body>
    <h1>{{ tv_name }} - 第 {{ season_number }} 季</h1>
    <ul>
{% for ep in episodes %}
    <li>
        第 {{ ep.episode_number }} 集 - {{ ep.name }}
        (<a href="{% url 'episode_detail' tv_id=tv_id season_number=season_number episode_number=ep.episode_number %}?tv_name={{ tv_name }}">查看字幕</a>)
    </li>
{% endfor %}
    </ul>
    <a href="{% url 'show_seasons' tv_id=tv_id %}">返回上一页</a>
</body>
</html>

```

## File: templates\index.html

- Extension: .html
- Language: html
- Size: 689 bytes
- Created: 2025-07-29 23:12:24
- Modified: 2025-07-29 23:29:30

### Code

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head><title>字幕查找系统</title></head>
<body>
    <h1>字幕查找系统</h1>
    <form method="get" action="/">
        <input type="text" name="query" placeholder="请输入美剧名称" value="{{ query|default:'' }}">
        <button type="submit">搜索</button>
    </form>

    {% if results %}
        <h2>搜索结果：</h2>
        <ul>
        {% for show in results %}
    <li>
        <a href="{% url 'show_seasons' tv_id=show.id %}">{{ show.name }}</a> (ID: {{ show.id }})
    </li>
{% empty %}
    <li>没有找到结果。</li>
{% endfor %}
        </ul>
    {% endif %}
</body>
</html>

```

## File: templates\seasons.html

- Extension: .html
- Language: html
- Size: 517 bytes
- Created: 2025-07-29 23:27:53
- Modified: 2025-07-29 23:33:51

### Code

```html
<!-- templates/seasons.html -->
<!DOCTYPE html>
<html>
<head><title>{{ tv_name }} - 所有季</title></head>
<body>
    <h1>{{ tv_name }} - 所有季</h1>
    <ul>
    {% for season in seasons %}
        <li>
            <a href="{% url 'show_episodes' tv_id=tv_id season_number=season.season_number %}">
                第 {{ season.season_number }} 季（{{ season.episode_count }} 集）
            </a>
        </li>
    {% endfor %}
    </ul>
    <a href="/">返回首页</a>
</body>
</html>

```

## File: templates\subtitle.html

- Extension: .html
- Language: html
- Size: 3231 bytes
- Created: 2025-07-29 23:39:56
- Modified: 2025-07-30 22:12:46

### Code

```html
<!-- templates/subtitle.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{{ tv_name }} S{{ season_number }}E{{ episode_number }} 字幕</title>
  <style>
    body { font-family: system-ui, Arial, sans-serif; line-height: 1.7; padding: 16px; }
    .line { margin: 8px 0; }
    .word { cursor: pointer; padding: 0 2px; border-radius: 4px; }
    .word:hover { background: #f0f0f0; }
    .bubble {
      position: fixed; max-width: 360px; background: #fff; border: 1px solid #ddd; border-radius: 8px;
      box-shadow: 0 6px 24px rgba(0,0,0,.12); padding: 12px; z-index: 9999;
    }
    .bubble h4 { margin: 0 0 6px 0; font-size: 16px; }
    .bubble small { color: #666; }
    .bubble .actions { margin-top: 8px; display: flex; gap: 8px; align-items: center; }
  </style>
</head>
<body>
  <h1>{{ tv_name }} - 第 {{ season_number }} 季 第 {{ episode_number }} 集 - 字幕</h1>

  <div id="subs">
    {% for seg in segments %}
      <div class="line" data-idx="{{ seg.index }}" data-start="{{ seg.start }}" data-end="{{ seg.end }}">
        {% for w in seg.words %}
          <span class="word" data-word="{{ w }}">{{ w }}</span>{% if not forloop.last %} {% endif %}
        {% endfor %}
      </div>
    {% endfor %}
  </div>

  <a href="/">返回首页</a>

  <div id="bubble" class="bubble" style="display:none;"></div>

  <script>
    const bubble = document.getElementById('bubble');

    function showBubble(html, x, y) {
      bubble.innerHTML = html;
      bubble.style.left = Math.min(x + 12, window.innerWidth - bubble.offsetWidth - 12) + 'px';
      bubble.style.top  = Math.min(y + 12, window.innerHeight - bubble.offsetHeight - 12) + 'px';
      bubble.style.display = 'block';
    }
    function hideBubble() { bubble.style.display = 'none'; }

    document.addEventListener('click', async (e) => {
      const w = e.target.closest('.word');
      if (!w) { hideBubble(); return; }
      const word = w.dataset.word;

      showBubble(`<small>加载中…</small>`, e.clientX, e.clientY);

      try {
        // 1) 翻译
        const tRes = await fetch(`/api/translate?word=${encodeURIComponent(word)}`);
        const tData = await tRes.json();
        if (!tRes.ok) throw new Error(tData.error || '翻译失败');

        // 2) TTS（生成/复用 wav）
        const aRes = await fetch(`/api/tts?word=${encodeURIComponent(word)}`);
        const aData = await aRes.json();
        if (!aRes.ok) throw new Error(aData.error || 'TTS 失败');

        const html = `
          <h4>${word}</h4>
          <div>${tData.text ? tData.text : '<small>无翻译</small>'}</div>
          <div class="actions">
            <audio id="ttsPlayer" src="${aData.url}" controls></audio>
          </div>
          <div><small>来源：googletrans / Windows SAPI</small></div>
        `;
        showBubble(html, e.clientX, e.clientY);
      } catch (err) {
        showBubble(`<small style="color:#c00;">${err.message}</small>`, e.clientX, e.clientY);
      }
    });

    // 点击外部关闭
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideBubble(); });
  </script>
</body>
</html>

```

