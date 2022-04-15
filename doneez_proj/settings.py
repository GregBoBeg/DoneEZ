"""
Django settings for doneez_proj project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path
import requests
from . import awssecrets

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Application Secrets
secret_name = "DoneEZDjangoSecrets"
region_name = "us-west-1"
appsecrets = awssecrets.get_secrets(secret_name, region_name)

# Django Secret Key
SECRET_KEY = appsecrets["DjangoSecretKey"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Host Security Whitelist
ALLOWED_HOSTS = [appsecrets["DjangoHost"], 'localhost']

# Grab the AWS Elastic Beanstalk Private IP and dynamically add it to the allowed hosts
EC2_PRIVATE_IP = None
try:
    security_token = requests.put(
        'http://169.254.169.254/latest/api/token',
        headers={'X-aws-ec2-metadata-token-ttl-seconds': '60'}).text
	
    EC2_PRIVATE_IP = requests.get(
        'http://169.254.169.254/latest/meta-data/local-ipv4',
        headers={'X-aws-ec2-metadata-token': security_token},
        timeout=0.01).text
except requests.exceptions.RequestException:
    pass

if EC2_PRIVATE_IP:
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)


# AWS SES Email Configuration, Secured with AWS Secrets Manager
DEFAULT_FROM_EMAIL = appsecrets["SESEmailFrom"]
EMAIL_BACKEND = appsecrets["SESEmailBackend"]
EMAIL_HOST = appsecrets["SESEmailHost"]
EMAIL_PORT = appsecrets["SESEmailPort"]
EMAIL_USE_TLS = True
EMAIL_HOST_USER = str(appsecrets["SESSMTPUsername"])
EMAIL_HOST_PASSWORD = str(appsecrets["SESSMTPPassword"])


# Set the default for how long session cookies will live = Seconds * Minutes * Hours * Days
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30

# Login paths
LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = '/dashboard/login/'


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Local Apps
    'doneez_app.apps.DoneezAppConfig',

    # DASHBOARD APP
    # In Django, it is customary to create a separate app for user accounts (typically called "Users" or "Accounts").
    # Since DoneEZ's users are businesses with needs beyond simple user account functionality, 
    # we have opted to use the name "Dashboard" for this app.
    'dashboard.apps.DashboardConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'doneez_proj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'doneez_proj.wsgi.application'


# Database Secrets
secret_name = "arn:aws:secretsmanager:us-west-1:990348361176:secret:DoneEZPostgresSecret-N1jk1N"
region_name = "us-west-1"
dbsecrets = awssecrets.get_secrets(secret_name, region_name)

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':   dbsecrets["engine"],
        'NAME':     dbsecrets["dbname"],
        'USER':     dbsecrets["username"],
        'PASSWORD': dbsecrets["password"],
        'HOST':     dbsecrets["host"],
        'PORT':     dbsecrets["port"],
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ---- STATIC FILES ---- #

# Static files (CSS, JavaScript, Images, etc)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATIC FILE SETTINGS FOR AWS DEPLOYMENTS:
STATIC_URL = '/static/'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT  = os.path.join(PROJECT_ROOT, 'doneez_app/static')
# STATIC_ROOT=os.path.join(BASE_DIR,'static/')

# Troubleshooting Result Notes:
# 04/09/2022 Note - AWS apparently changed the static files namespace 
#   from:
#       "aws:elasticbeanstalk:container:python:staticfiles"  
#   to:
#       "aws:elasticbeanstalk:environment:proxy:staticfiles"
# This requires the AWS Config files to be updated for deployment purposes.


# Media Files
# Change the default location of where media & image files are located
MEDIA_ROOT = os.path.join(BASE_DIR, 'doneez_app/media')
MEDIA_URL = '/media/'

