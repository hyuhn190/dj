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
