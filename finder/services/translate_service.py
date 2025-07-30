# finder/services/translate_service.py
import time, random
from django.core.cache import cache
from django.conf import settings

# deep-translator 兜底（如果可用）
try:
    from deep_translator import GoogleTranslator as DTGoogle
    _USE_DEEP = True
except Exception:
    _USE_DEEP = False

from googletrans import Translator

DEFAULT_SERVICE_URLS = getattr(settings, "GOOGLETRANS_SERVICE_URLS", [
    "translate.google.com",
    "translate.google.com.hk",
    "translate.googleapis.com",
])
REQUEST_TIMEOUT = int(getattr(settings, "GOOGLETRANS_TIMEOUT", 5))
CACHE_TTL = int(getattr(settings, "TRANSLATE_CACHE_TTL", 60 * 60))  # 1h

def _make_translator(urls):
    t = Translator(service_urls=urls, raise_exception=True)
    # 兼容属性名差异（与你当前视图实现保持一致）
    if not hasattr(t, 'raise_exception'):
        setattr(t, 'raise_exception', True)
    if not hasattr(t, 'raise_Exception'):
        setattr(t, 'raise_Exception', True)
    return t

class TranslateService:
    """
    负责将"多域名轮换 + 重试 + 兜底 + 缓存"封装为一个可复用的服务。
    """

    def __init__(self, service_urls=None, cache_prefix="trans:"):
        self.service_urls = list(service_urls or DEFAULT_SERVICE_URLS)
        self.cache_prefix = cache_prefix
        # 预加载高频词汇
        self._preload_common_words()

    def _preload_common_words(self):
        """
        预加载高频词汇到缓存
        """
        common_words = ['hello', 'world', 'good', 'morning', 'thank you', 'please', 'yes', 'no']
        for word in common_words:
            cache_key = f"{self.cache_prefix}en:zh-cn:{word.lower()}"
            if not cache.get(cache_key):
                try:
                    # 异步预加载，避免阻塞
                    self.translate(word)
                except:
                    pass  # 忽略预加载错误

    def _translate_with_failover(self, word, src='en', dest='zh-cn', max_total_attempts=6):
        urls_round = self.service_urls.copy()
        random.shuffle(urls_round)
        last_err = None
        attempts = 0
        for base in urls_round:
            tr = _make_translator([base])
            for _ in range(2):  # 每个域名尝试 2 次（与你当前实现一致）
                attempts += 1
                if attempts > max_total_attempts:
                    break
                try:
                    res = tr.translate(word, src=src, dest=dest)  # requests 超时由底层控制
                    return res.text
                except Exception as e:
                    last_err = e
                    time.sleep(0.2)
            if attempts > max_total_attempts:
                break
        if last_err:
            raise last_err
        raise RuntimeError("translation failed with no specific error")

    def translate(self, word: str, src='en', dest='zh-cn') -> dict:
        # 使用更细粒度的缓存键
        cache_key = f"{self.cache_prefix}{src}:{dest}:{word.lower()}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # 先试 googletrans + 域名轮换
        try:
            text = self._translate_with_failover(word, src=src, dest=dest, max_total_attempts=6)
            data = {"word": word, "src": src, "dest": dest, "text": text, "engine": "googletrans"}
            # 根据词长度设置不同的过期时间
            expire_time = 7*24*60*60 if len(word) < 5 else 24*60*60
            cache.set(cache_key, data, expire_time)
            return data
        except Exception as e_gt:
            # 兜底 deep-translator（与当前实现一致）
            if _USE_DEEP:
                try:
                    text = DTGoogle(source=src, target=dest).translate(word)
                    data = {"word": word, "src": src, "dest": dest, "text": text, "engine": "deep-translator"}
                    expire_time = 7*24*60*60 if len(word) < 5 else 24*60*60
                    cache.set(cache_key, data, expire_time)
                    return data
                except Exception:
                    pass
            # 两者都失败，返回错误信息（视图将据此设置 502）
            return {"word": word, "error": f"{type(e_gt).__name__}: {e_gt}"}
