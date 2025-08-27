import os

from dropbox.exceptions import ApiError
from storages.backends.dropbox import DropboxStorage
from storages.utils import safe_join
from django.core.cache import cache


class WindowsCompatibleDropboxStorage(DropboxStorage):
    CACHE_TTL = 60 * 60 * 4 - 30

    def _full_path(self, name):
        if name == "/":
            name = ""

        if os.name == "nt":
            return os.path.join("/", self.root_path, name).replace("\\", "/")
        else:
            return safe_join(self.root_path, name).replace("\\", "/")

    # @staticmethod
    # def _get_cache_key(name: str) -> str:
    #     return f"dropbox:media:{name}"

    # def url(self, name):
    #     cache_key = self._get_cache_key(name)
    #     if link := cache.get(cache_key):
    #         return link

    #     try:
    #         res = self.client.files_get_temporary_link(self._full_path(name))
    #         link = res.link
    #         cache.set(cache_key, link, self.CACHE_TTL)
    #         return link
    #     except ApiError:
    #         return None
