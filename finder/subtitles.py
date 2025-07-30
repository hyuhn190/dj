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

