"""
Django settings for rateapp project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from datetime import timedelta
import dj_database_url
import storages
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # 3rd party
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'dj_rest_auth.registration',
    'dj_rest_auth',
    'corsheaders',
    'braces',
    'allauth.socialaccount',
    'storages',
    'fcm_django',

    # local
    'users',
    'api',
    'comments',
    'posts',

]

AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

]

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rateapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
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

WSGI_APPLICATION = 'rateapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rateet_db',
        'USER': 'rateetadmin',
        'PASSWORD': '5451051atabar',
        'HOST': 'rateet-db-1.cz39flew78tj.us-east-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

#set S3 as the place to store your files.
DEFAULT_FILE_STORAGE = 'rateapp.storage_backends.MediaStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

AWS_QUERYSTRING_AUTH = False #This will make sure that the file URL does not have unnecessary parameters like your access key.
AWS_S3_CUSTOM_DOMAIN = AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

AWS_S3_FILE_OVERWRITE = False

#static media settings
STATIC_URL = 'https://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/static/'
MEDIA_URL = 'https://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/media/'

STATICFILES_DIRS = ( os.path.join(BASE_DIR, 'static'), )
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
# STATICFILES_FINDERS = (
# ‘django.contrib.staticfiles.finders.FileSystemFinder’,
# ‘django.contrib.staticfiles.finders.AppDirectoriesFinder’,
# )

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8
        }
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # {
    #     'NAME': 'rateapp.validators.UppercaseValidator',
    # },
]

PASSWORD_RESET_TIMEOUT_DAYS = 1


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)s
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# WHITENOISE_USE_FINDERS = True
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
#
# STATIC_URL = '/static/'

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'

ADMINS = [('Baris', 'no.reply.rateet@gmail.com'),]
MANAGERS = ADMINS


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'no.reply.rateet@gmail.com'
EMAIL_HOST_PASSWORD = config('GMAIL_APP_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Rateet <noreply@rateet.com>'


AUTH_USER_MODEL = 'users.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':[
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}

REST_AUTH_REGISTER_SERIALIZERS = {
        'REGISTER_SERIALIZER': 'api.serializers.UserRegisterSerializer'
}

REST_AUTH_SERIALIZERS = {
        'USER_DETAILS_SERIALIZER': 'api.serializers.UserSerializer',
        'LOGIN_SERIALIZER': 'api.serializers.UserLoginSerializer',
        'PASSWORD_RESET_SERIALIZER': 'api.serializers.PasswordResetSerializer'
}

SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(days=300),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=300),
        'ROTATE_REFRESH_TOKENS': True,
        'AUTH_HEADER_TYPES': ('Bearer',)
}


# CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080'
)

REST_USE_JWT = True

# JWT_AUTH_COOKIE = 'myHttpOnlyCookie'
#
# JWT_AUTH_SECURE = True
#
# JWT_AUTH_SAMESITE = 'Strict'

# CSRF_COOKIE_NAME = "csrftoken"
#
# CSRF_COOKIE_HTTPONLY = False
#
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True
#
# SESSION_COOKIE_NAME = "session-cookie"

#ALLAUTH SETTINGS
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none" #make it mandatory or optional in production!! use amazon-ses or sendinblue
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 500
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_MIN_LENGTH = 2
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True


#DJ REST AUTH SETTINGS
LOGOUT_ON_PASSWORD_CHANGE = False


FCM_DJANGO_SETTINGS = {
         # default: _('FCM Django')
        "APP_VERBOSE_NAME": "FCM DEVICES",
         # Your firebase API KEY
        "FCM_SERVER_KEY": config('FCM_SERVER_KEY'),
         # true if you want to have only one active device per registered user at a time
         # default: False
        "ONE_DEVICE_PER_USER": False,
         # devices to which notifications cannot be sent,
         # are deleted upon receiving error response from FCM
         # default: False
        "DELETE_INACTIVE_DEVICES": False,
}

#production
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_SSL_REDIRECT = False # check this later!
SECURE_HSTS_SECONDS = 0 #check this later!

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880 # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880 # 5 MB
