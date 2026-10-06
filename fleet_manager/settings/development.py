from .base import *


SECRET_KEY = (
    "django-insecure-^@l@yfpc*u)26g@0(51c%j3x6qr#r(dvx8)"
    "a9%67&m-=d3jn-4"
)

DEBUG = True

ALLOWED_HOSTS = []


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
