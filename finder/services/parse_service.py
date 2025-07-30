# finder/services/parse_service.py
from ..subtitle_parser import parse_srt_to_segments

class ParseService:
    """
    对解析器做一层轻封装，便于将来替换或预处理。
    """
    def parse_srt(self, file_path: str):
        return parse_srt_to_segments(file_path)
