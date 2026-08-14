"""Settings used by pytest-django (see pytest.ini). Same shape as dev, just
explicit so CI/test runs never accidentally pick up prod.py behavior."""
from .dev import *  # noqa: F401,F403

DEBUG = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
