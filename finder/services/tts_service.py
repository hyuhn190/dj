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
