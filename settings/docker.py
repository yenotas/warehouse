from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'warehouse_db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'gjcnu_1827'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = ['192.168.186.14', 'localhost', '127.0.0.1']

INTERNAL_IPS = [
    "127.0.0.1",
    "192.168.186.14",
]