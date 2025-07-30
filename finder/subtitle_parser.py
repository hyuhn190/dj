# finder/subtitle_parser.py
import re
import pysrt

WORD_RE = re.compile(r"[A-Za-z]+'[A-Za-z]+|[A-Za-z]+")

def parse_srt_to_segments(file_path: str):
    """
    读取 .srt ，按条目解析，返回：
    [
      { "index": 1, "start": "00:00:01,000", "end": "00:00:02,000",
        "text": "Hello world!", "words": ["Hello","world"] },
      ...
    ]
    """
    subs = pysrt.open(file_path, encoding='utf-8', error_handling='ignore')
    segments = []
    for item in subs:
        # 去掉简单的斜体标签；复杂 HTML 可再做清洗
        text = (item.text or "").replace("<i>", "").replace("</i>", "")
        words = WORD_RE.findall(text)
        segments.append({
            "index": item.index,
            "start": str(item.start),
            "end": str(item.end),
            "text": text,
            "words": words,
        })
    return segments

def parse_srt_generator(file_path: str):
    """
    生成器版本的字幕解析，节省内存
    """
    subs = pysrt.open(file_path, encoding='utf-8', error_handling='ignore')
    for item in subs:
        # 去掉简单的斜体标签；复杂 HTML 可再做清洗
        text = (item.text or "").replace("<i>", "").replace("</i>", "")
        words = WORD_RE.findall(text)
        yield {
            "index": item.index,
            "start": str(item.start),
            "end": str(item.end),
            "text": text,
            "words": words,
        }
