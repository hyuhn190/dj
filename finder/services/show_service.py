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