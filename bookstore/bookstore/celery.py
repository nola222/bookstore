# #使用消息队列celery来异步发邮件
# from __future__ import absolute_import,unicode_literals
# import os
# from celery import Celery
# #设置默认的Django设置模块的“celery”程序
# os.environ.setdefault('DJANGO_SETTINGS_MODULE','bookstore.settings')
# app = Celery('bookstore',broker='redis://127.0.0.1:6379/6')
# #使用字符串意味着程序员不需要序列化
# #配置对象的子过程。
# #空间= 'celery”意味着所有的celery相关配置的钥匙
# #应该有一个` celery_ `前缀。
# app.config_from_object('django.conf:settings',namespace='CELERY')
# #从所有注册Django程序配置#负荷任务模块
# app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print('Request:{0!r}'.format(self.request))

# bookstore/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')

app = Celery('bookstore', broker='redis://127.0.0.1:6379/6')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))