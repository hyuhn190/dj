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
