
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

import os
from datetime import timedelta

load_dotenv()


def env_list(name, default=None):
    value = os.getenv(name)
    if value:
        return [item.strip() for item in value.split(',') if item.strip()]
    return list(default) if default else []

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True
LOCAL_SERVER= os.getenv('LOCAL_SERVER','FALSE') == 'True'
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
] + os.getenv('ALLOWED_HOSTS', '').split(',')

# Application definition
DJ_DEFAULT_INSTALLED_APPS=[
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS=[
    'django_extensions',
     "rest_framework",
    "rest_framework.authtoken",
    'corsheaders',
    'whitenoise.runserver_nostatic',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'oauth2_provider',
    'drf_yasg',
    'djoser',
    'social_django',
    'cities_light',
]
CORE_APPS = [
    'mainapps.accounts',
    'mainapps.profiles',
]

INSTALLED_APPS= DJ_DEFAULT_INSTALLED_APPS+THIRD_PARTY_APPS+CORE_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
   
]


ROOT_URLCONF = 'core.urls'
AUTH_USER_MODEL = 'accounts.User' 
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/"templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.branding',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
PLATFORM_NAME = os.getenv('PLATFORM_NAME') or os.getenv('SITE_NAME') or 'Platform'
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
DEFAULT_FROM_EMAIL =f"{PLATFORM_NAME} <{EMAIL_HOST_USER}>"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'





STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  

STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static'),
]

MEDIA_URL = '/media/'
MEDIAFILES_DIRS=[os.path.join(BASE_DIR,'media')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_STATIC_LOCATION = os.getenv('AWS_STATIC_LOCATION', 'users/static')
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_S3_CONNECT_TIMEOUT = 10  
AWS_S3_TIMEOUT = 60 
AWS_S3_FILE_OVERWRITE = True

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:

    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {"location": AWS_STATIC_LOCATION},
        },
    }
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"


SITE_URL=os.getenv('SITE_URL','http://localhost:8080')
SITE_NAME = os.getenv('SITE_NAME') or PLATFORM_NAME
FRONTEND_DOMAIN=os.getenv('FRONTEND_DOMAIN')




AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    "djoser.auth_backends.LoginFieldBackend",
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.microsoft.MicrosoftOAuth2'
]
# DJOSER CONFIGURATION
DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'accounts/password_reset/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'EMAIL_FRONTEND_SITE_NAME': SITE_NAME,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'LOGOUT_ON_PASSWORD_CHANGE': True,
    'EMAIL_FRONTEND_DOMAIN':FRONTEND_DOMAIN,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
    'EMAIL_FRONTEND_PROTOCOL':'https' if not LOCAL_SERVER else 'http',
    # Use SimpleJWT instead of DRF authtoken
    'TOKEN_MODEL': None,
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': os.getenv('REDIRECT_URIS', '').split(','),
    'SERIALIZERS': {
        'token_create': 'mainapps.accounts.serializers.MyTokenObtainPairSerializer',
        'token': 'mainapps.accounts.serializers.MyTokenObtainPairSerializer',
        'token_refresh': 'mainapps.accounts.serializers.TokenRefreshSerializer',
        'provider_auth': 'mainapps.accounts.serializers.SocialJWTSerializer',
        'user_create': 'mainapps.accounts.serializers.UserCreateSerializer',
        'user': 'mainapps.accounts.serializers.UserSerializer',
    },
    'SOCIAL_AUTH_TOKEN_STRATEGY': 'mainapps.accounts.social.CustomSocialTokenStrategy',
}

SERIALIZERS={
    'user_create': 'mainapps.accounts.serializers.UserCreateSerializer',
    'user': 'mainapps.accounts.serializers.UserSerializer',
    'provider_auth': 'mainapps.accounts.serializers.SocialJWTSerializer'

}
# socials with djoser
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_AUTH_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_AUTH_SECRET_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ['first_name', 'last_name']

SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('FACEBOOK_AUTH_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('FACEBOOK_AUTH_SECRET_KEY')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'email, first_name, last_name'
}

SOCIAL_AUTH_MICROSOFT_GRAPH_KEY = os.getenv('MICROSOFT_AUTH_KEY')
SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET = os.getenv('MICROSOFT_AUTH_SECRET_KEY')



SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=50),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    "TOKEN_OBTAIN_SERIALIZER": "mainapps.accounts.serializers.MyTokenObtainPairSerializer",

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

AUTH_COOKIE='access'
AUTH_COOKIE_ACCESS_MAX_AGE=60*10
AUTH_COOKIE_REFRESH_MAX_AGE=60*60*24
AUTH_COOKIE_MAX_AGE=60*60*24
AUTH_COOKIE_SECURE=False 
AUTH_COOKIE_HTTP_ONLY=True
AUTH_COOKIE_PATH='/'
AUTH_COOKIE_SAMESITE='None'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'mainapps.accounts.authentication.AccountJWTAuthentication',
    )
}


CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

LOCAL_FRONTEND_URLS = env_list('LOCAL_FRONTEND_URLS', ["http://localhost:8080"])
DEV_FRONTEND_URLS = env_list('DEV_FRONTEND_URLS', [])
PRODUCTION_FRONTEND_URLS = env_list('PRODUCTION_FRONTEND_URLS', [])

cors_origins = LOCAL_FRONTEND_URLS + DEV_FRONTEND_URLS + PRODUCTION_FRONTEND_URLS
if SITE_URL:
    cors_origins.append(SITE_URL.rstrip('/'))
CORS_ALLOWED_ORIGINS = cors_origins

csrf_trusted_origins = LOCAL_FRONTEND_URLS + DEV_FRONTEND_URLS + PRODUCTION_FRONTEND_URLS
if SITE_URL:
    csrf_trusted_origins.append(SITE_URL.rstrip('/'))
CSRF_TRUSTED_ORIGINS = csrf_trusted_origins



SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = not LOCAL_SERVER
SESSION_COOKIE_SECURE = not LOCAL_SERVER
CSRF_COOKIE_SECURE = not LOCAL_SERVER

SESSION_COOKIE_SAMESITE = "None" if not LOCAL_SERVER else "Lax"
CSRF_COOKIE_SAMESITE   = "None" if not LOCAL_SERVER else "Lax"

CORS_ALLOW_CREDENTIALS = True

FILE_UPLOAD_TIMEOUT = 3600
DATA_UPLOAD_MAX_MEMORY_SIZE = 2147483648  # 2GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 2147483648  # 2GB


USE_L10N = True
USE_THOUSAND_SEPARATOR = True


STRIPE_PUP_KEY = os.getenv('STRIPE_PUP_KEY')
STRIPE_SEC_KEY = os.getenv('STRIPE_SEC_KEY')
STRIPE_ENDPOINT_SECRET = os.getenv('STRIPE_ENDPOINT_SECRET')
BASIC_PLAN_ID = os.getenv('BASIC_PLAN_ID')
PRO_PLAN_ID = os.getenv('PRO_PLAN_ID')
PREMIUM_PLAN_ID =  os.getenv('PREMIUM_PLAN_ID')

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '16.171.249.33:9092')
