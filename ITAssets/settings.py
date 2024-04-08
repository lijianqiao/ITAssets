from dotenv import load_dotenv
import os
from pathlib import Path
from .simpleui_conf import *

# 加载环境变量
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_URL = os.getenv("PUBLIC_URL", default="http://localhost:8020")

SECRET_KEY = os.getenv("SECRET_KEY")

# 安全警告：不要在生产环境中打开调试的情况下运行！
DEBUG = True if 'True' == os.getenv("DEBUG") else False  # 是否开启调试模式

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(',')  # 允许访问的主机

INSTALLED_APPS = [
    "simpleui",  # 使用simpleui
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'assets.apps.AssetsConfig',  # 资产管理
    'repair.apps.RepairConfig',  # 维修管理
    "corsheaders",  # 跨域请求
    'import_export',  # 导入导出
    'auditlog',  # 审计日志
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    'django.middleware.locale.LocaleMiddleware',  # 国际化
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # 跨域请求
    'auditlog.middleware.AuditlogMiddleware',  # 审计日志
]

ROOT_URLCONF = "ITAssets.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ITAssets.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': os.getenv("DATABASE_ENGINE"),
        'NAME': os.getenv("DATABASE_NAME"),
        'USER': os.getenv("DATABASE_USER"),
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': os.getenv("DATABASE_HOST"),
        'PORT': os.getenv("DATABASE_PORT"),
        'OPTIONS': {
            'charset': 'utf8mb4',  # 设置字符集, 要确保数据库支持并设置为utf8mb4
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,  # 密码最小长度
        }
    },
]

# 解决django 跨域问题
CORS_ALLOW_CREDENTIALS = True if 'True' == os.getenv("CORS_ALLOW_CREDENTIALS") else False  # 允许携带cookie
SECURE_CROSS_ORIGIN_OPENER_POLICY = os.getenv("SECURE_CROSS_ORIGIN_OPENER_POLICY")  # 设置跨域策略
CSRF_TRUSTED_ORIGINS = [os.getenv("PUBLIC_URL")]  # 允许跨域的域名

# 设置会话过期时间
SESSION_EXPIRE_SECONDS = int(os.getenv("SESSION_EXPIRE_SECONDS"))  # 7天
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True if 'True' == os.getenv(
    "SESSION_EXPIRE_AFTER_LAST_ACTIVITY") else False  # 会话过期时间是否从最后一次活动开始计算
SESSION_TiMEOUT_REDIRECT_URL = '/login/'  # 会话过期后跳转的URL

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "zh-hans")

TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Shanghai")

USE_I18N = True

USE_TZ = False

STATIC_URL = os.getenv("STATIC_URL", "/static/")
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets/static"),
]

MEDIA_URL = os.getenv("MEDIA_URL", "/media/")

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
