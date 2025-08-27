import os
import logging

from dropbox.exceptions import ApiError
from storages.backends.dropbox import DropboxStorage
from storages.utils import safe_join
from django.core.cache import cache

logger = logging.getLogger(__name__)


class WindowsCompatibleDropboxStorage(DropboxStorage):
    CACHE_TTL = 60 * 60 * 4 - 30

    # def _full_path(self, name):
    #     if name == "/":
    #         name = ""

    #     if os.name == "nt":
    #         return os.path.join("/", self.root_path, name).replace("\\", "/")
    #     else:
    #         return safe_join(self.root_path, name).replace("\\", "/")

    # def url(self, name):
    #     try:
    #         res = self.client.files_get_temporary_link(self._full_path(name))
    #         return res.link
    #     except ApiError as e:
    #         logger.error(f"Dropbox ApiError in url() for '{name}': {e}")
    #         return None
    #     except Exception as e:
    #         logger.error(f"General error in url() for '{name}': {e}")
    #         return None
