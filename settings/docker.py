from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '5432',
    }
}

SERV = os.getenv('SERV')

ALLOWED_HOSTS = [SERV, 'localhost', '127.0.0.1']

INTERNAL_IPS = [
    '127.0.0.1',
    SERV,
]
