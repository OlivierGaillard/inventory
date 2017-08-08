"""
Django settings for boutique project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.conf.global_settings import USE_THOUSAND_SEPARATOR, MEDIA_ROOT,\
    MEDIA_URL


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# base_dir = /home/olivier/DjangoMusic/boutique


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+^zq_ae12ud1bj-jqv%^jh=wu6z*oei$s6cnkwz%sohrq5ln$$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

LOGIN_REDIRECT_URL = '/'
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admindocs',
    'crispy_forms',
    'mptt',
    'django_mptt_admin',
    'products.apps.ProductsConfig',
    'finance.apps.FinanceConfig',
    'coordinates.apps.CoordinatesConfig',
    'accessories.apps.AccessoriesConfig',
    'clothes.apps.ClothesConfig',
    'shoes.apps.ShoesConfig',
    'accounts.apps.AccountsConfig',
    'thumbnails',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boutique.urls'

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
                'django.template.context_processors.static',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'boutique.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'fr-ch'

TIME_ZONE = 'Europe/Zurich'

USE_I18N = True

USE_L10N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True
DATE_FORMAT = ['%d/%m/%Y', '%d-%m-%Y']
SHORT_DATE_FORMAT = ['%d-%m-%Y']
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%d.%m.%Y', '%d-%m-%Y', '%d %m %Y',
    '%d/%m/%y', '%d.%m.%y', '%d-%m-%y', '%d %m %y',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/'


# Openexchangerates ID
CURRENCYSERVICE_ID = 'your open currency service id'
CURRENCY_RATES_FILE = 'finance/rates.txt'
CURRENCY_LIST_FILE  = 'finance/currencies.txt'


DJANGO_MONEY_RATES = {
    'DEFAULT_BACKEND': 'djmoney_rates.backends.OpenExchangeBackend',
    'OPENEXCHANGE_URL': 'http://openexchangerates.org/api/latest.json',
    'OPENEXCHANGE_APP_ID': 'your open exchange app id',
    'OPENEXCHANGE_BASE_CURRENCY': 'USD',
}




