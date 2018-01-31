"""
Django settings for bookstore project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7e-_$8n)*nbkw5hf20gcf0p9-2o&n4g+ocou5sbuw7x7b1-yp9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',#用户模块
    'books',#商品模块
    'tinymce',#富文本模块
    'cart',#购物车模块
    'order',#订单模块
    'haystack',#全文检索
    'users.templatetags.filters',#过滤器功能
    'comments',#评论模块
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'bookstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookstore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookstore',
        'USER': 'atguigu_test',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': 3306,
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static'),#调试时使用的静态文件目录
]

#富文本编辑配置项
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400,
}

#设置图片存放目录
MEDIA_ROOT = os.path.join(BASE_DIR,'static')

#配置redis缓存
CACHES = {
    'default':{
        'BACKEND':'django_redis.cache.RedisCache',
        'LOCATION':'redis://localhost:6379/2',
        'OPTIONS':{
            'CLIENT_CLASS':'django_redis.client.DefaultClient',
            'PASSWORD':''
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
#设置session_cache的别名
SESSION_CACHE_ALIAS = 'default'

#全文检索配置
HAYSTACK_CONNECTIONS = {
    'default':{
        #使用whoosh引擎
        'ENGINE':'haystack.backends.whoosh_cn_backend.WhooshEngine',
        #'ENGINE':'haystack.backends.whoosh_backend.WhooshEngine',
        #索引文件路径
        'PATH':os.path.join(BASE_DIR,'whoosh_index')
    }
}

#当添加 修改 删除数据时,自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 6#指定搜索结果每页的条数


#配置邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = '17319377060@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'mingJI2016'
# 收件人看到的发件人
EMAIL_FROM = 'shangguigu<17319377060@163.com>'


