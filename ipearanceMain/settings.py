"""
Django settings for ipearanceMain project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os

import django_heroku
import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z1xg6nv(ji*01%yq98+e#07@&lt6u#*l1xcj1ib3xba(lyk^ui'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fontawesome-free',
    #'datetimeutc',
    'rest_framework',
    'reset_migrations',
    'corsheaders',
    'ipearanceFront',
    'ipearanceBackend',
    
]

CORS_ORIGIN_ALLOW_ALL = True # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
CORS_ALLOW_CREDENTIALS = True


# CORS_ORIGIN_WHITELIST = (
#         #  'localhost:3000/'
#         'http://localhost:3000',
#         'http://192.168.10.111:3000',
#         'http://192.168.10.20:3001',
        
#      )

REST_FRAMEWORK = {
     #'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.IsAdminUser',
        #  'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        # 'rest_framework.permissions.DjangoModelPermissions',
        
   # ),
   # 'DEFAULT_RENDERER_CLASSES': (
#         'rest_framework.renderers.JSONRenderer',
    #)
	'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
 }


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ipearanceMain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # where all templates html  files are located--> /templates on application folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'ipearanceMain.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': { 
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'dbIP4', 
#         'USER': 'postgres', 
#         'PASSWORD': '1',
#         'HOST': '127.0.0.1', 
#         'PORT': '5432',
#     }
# }


DATABASES = {
default: dj_database_url.config()
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 3}
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]







# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'el'

TIME_ZONE = 'Europe/Athens'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_SECONDS = 5000
SESSION_SAVE_EVERY_REQUEST = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# where all css,js and images files are located--> /static on application folder
STATIC_URL = 'ipearanceFront/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )
STATIC_ROOT = os.path.join(BASE_DIR,  'ipearanceFront/static')

# where all excel  files are located--> /media on application folder
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'ipearanceFront/media')
django_heroku.settings(locals())

AUTH_USER_MODEL = 'ipearanceBackend.Users'   #our custom auth model, very important
LOGIN_REDIRECT_URL = 'welcome'# after login redirect,very important
LOGOUT_REDIRECT_URL = 'pagelogin' #after logout where the user will land page
LOGIN_URL='pagelogin'# after unauthorized action to redirect to login page,very important

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
from django.contrib.messages import constants as messages
MESSAGE_LEVEL = 10  # DEBUG
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}