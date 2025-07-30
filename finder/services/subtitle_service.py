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
