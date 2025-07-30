# Table of Contents
- .env
- db.sqlite3
- manage.py
- finder\admin.py
- finder\apps.py
- finder\models.py
- finder\subtitles.py
- finder\tests.py
- finder\tmdb.py
- finder\urls.py
- finder\views.py
- finder\__init__.py
- finder\migrations\__init__.py
- subtitle_project\asgi.py
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
- Size: 5874 bytes
- Created: 2025-07-29 23:38:08
- Modified: 2025-07-30 00:37:23

### Code

```python
import requests
import json
import os

API_KEY = "DQ0O7m6MVqAtQXvcJ7c6CdCunFwmnIIV"
APP_NAME = "testapi"
APP_VERSION = "1"


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
        resp = requests.get(url, headers=headers, params=params)

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
        resp = requests.post(url, headers=headers, json=data)

        if resp.status_code == 200:
            download_info = resp.json()
            download_link = download_info.get('link')

            if download_link:
                # 下载字幕文件
                subtitle_resp = requests.get(download_link)

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

    # 按集数分组字幕
    episodes_subtitles = {}

    for subtitle in results['data']:
        attr = subtitle['attributes']

        # 确保是英文字幕
        if attr['language'] == 'en':
            episode_num = attr['feature_details']['episode_number']

            # 按集数分组
            if episode_num not in episodes_subtitles:
                episodes_subtitles[episode_num] = []
            episodes_subtitles[episode_num].append(subtitle)

    # 为每集选择最佳字幕并下载
    downloaded_count = 0

    for episode_num in sorted(episodes_subtitles.keys()):
        # 选择该集的最佳字幕
        best_subtitle = select_best_subtitle(episodes_subtitles[episode_num])

        if best_subtitle:
            attr = best_subtitle['attributes']
            file_id = attr['files'][0]['file_id']

            # 创建统一的文件命名规则: SxxExx.srt
            file_name = f"S{season:02d}E{episode_num:02d}.srt"

            # 下载字幕文件
            if download_subtitle_file(file_id, file_name, save_directory):
                downloaded_count += 1
                print(f"第 {episode_num} 集最佳字幕下载完成")

    print(f"成功下载了 {downloaded_count} 个字幕文件到 {save_directory}")
    print("文件命名规则: SxxExx.srt (例如: S01E01.srt)")

if __name__ == "__main__":
    # 为《绝命毒师》第一季每集下载一个最佳英文字幕文件
    save_directory = r"C:\Users\hy303\Desktop\breaking_bad_subtitles"
    download_season_subtitles_single("Breaking Bad", 4, save_directory)


```

## File: finder\tests.py

- Extension: .py
- Language: python
- Size: 63 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-29 23:10:16

### Code

```python
from django.test import TestCase

# Create your tests here.

```

## File: finder\tmdb.py

- Extension: .py
- Language: python
- Size: 864 bytes
- Created: 2025-07-29 23:13:51
- Modified: 2025-07-29 23:33:15

### Code

```python
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


```

## File: finder\urls.py

- Extension: .py
- Language: python
- Size: 465 bytes
- Created: 2025-07-29 23:11:27
- Modified: 2025-07-30 00:21:35

### Code

```python
# finder/urls.py
from django.urls import path
from . import views


# finder/urls.py
urlpatterns = [
    path('', views.index, name='index'),
    path('show/<int:tv_id>/', views.show_seasons, name='show_seasons'),
    path('show/<int:tv_id>/season/<int:season_number>/', views.show_episodes, name='show_episodes'),
    path('show/<int:tv_id>/season/<int:season_number>/episode/<int:episode_number>/', views.episode_detail, name='episode_detail'),
]



```

## File: finder\views.py

- Extension: .py
- Language: python
- Size: 2490 bytes
- Created: 2025-07-29 23:10:16
- Modified: 2025-07-30 00:38:35

### Code

```python
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

## File: subtitle_project\settings.py

- Extension: .py
- Language: python
- Size: 3455 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-29 23:11:12

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
```

## File: subtitle_project\urls.py

- Extension: .py
- Language: python
- Size: 200 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-29 23:14:23

### Code

```python
# subtitle_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('finder.urls')),
    path('admin/', admin.site.urls),
]

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
- Size: 0 bytes
- Created: 2025-07-29 23:10:13
- Modified: 2025-07-29 23:10:13

### Code

```python

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
- Size: 454 bytes
- Created: 2025-07-29 23:39:56
- Modified: 2025-07-29 23:40:05

### Code

```html
<!-- templates/subtitle.html -->
<!DOCTYPE html>
<html>
<head><title>{{ tv_name }} S{{ season_number }}E{{ episode_number }} 字幕</title></head>
<body>
    <h1>{{ tv_name }} - 第 {{ season_number }} 季 第 {{ episode_number }} 集 - 字幕内容</h1>
    <div style="white-space: pre-wrap;">
        {% for line in subtitles %}
            {{ line }}<br>
        {% endfor %}
    </div>
    <a href="/">返回首页</a>
</body>
</html>

```

