import os

from .base import *


DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# enabling dropbox windows support for development
STORAGES["default"]["BACKEND"] = "base.storages.WindowsCompatibleDropboxStorage"
