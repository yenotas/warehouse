from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'PORT': os.getenv('DATABASE_PORT'),
        'HOST': 'localhost',
    }
}

print('DATABASE', DATABASES['default'])

ALLOWED_HOSTS = ['localhost', '127.0.0.1', os.getenv('ALLOWED_HOSTS')]
print('ALLOWED_HOSTS', ALLOWED_HOSTS)

CORS_ALLOWED_ORIGINS = [
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    'https://' + os.getenv('ALLOWED_HOSTS')
]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

print('CORS_ALLOWED_ORIGINS', CORS_ALLOWED_ORIGINS)

INTERNAL_IPS = ALLOWED_HOSTS

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
CORS_ORIGIN_ALLOW_ALL = True

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'debug.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }