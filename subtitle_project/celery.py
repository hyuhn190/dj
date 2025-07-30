# subtitle_project/celery.py
import os
from celery import Celery

# 设置Django的设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subtitle_project.settings')

app = Celery('subtitle_project')

# 使用Django设置中的配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()
