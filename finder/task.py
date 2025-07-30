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
