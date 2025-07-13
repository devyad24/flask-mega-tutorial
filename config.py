import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    MAIL_SERVER = os.environ.get('MAIL_SERVER') 
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['plebman4211@gmail.com', 'devyadav4211@gmail.com']
    MAIL_SENDER = 'devyadav4211@gmail.com'
    POSTS_PER_PAGE = 20
    LANGUAGES = ['en', 'es', 'hi']
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    CACHE_HOST_URL = os.environ.get('CACHE_HOST_URL') or 'redis://'
    CELERY = dict(
        broker_url=os.environ.get('CACHE_HOST_URL'),
        result_backend=os.environ.get('CACHE_HOST_URL'),
        task_ignore_result=False,
    )