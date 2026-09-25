"""
Settings para la suite de tests (pytest y CI): no requieren Redis y usan sqlite
en memoria salvo que se defina TEST_DATABASE_URL.
"""
import os

os.environ.setdefault('SECRET_KEY', 'clave-solo-para-tests')

import dj_database_url  # noqa: E402

from .settings import *  # noqa: E402,F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# El CI define TEST_DATABASE_URL para ejecutar los tests sobre Postgres, igual que producción.
if os.environ.get('TEST_DATABASE_URL'):
    DATABASES['default'] = dj_database_url.parse(os.environ['TEST_DATABASE_URL'])

# Caché local por proceso; conftest.py la vacía antes de cada test.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Hash de contraseñas rápido para acelerar los tests.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
