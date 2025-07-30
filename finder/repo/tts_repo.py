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
