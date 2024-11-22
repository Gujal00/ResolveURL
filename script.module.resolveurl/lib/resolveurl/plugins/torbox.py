"""
    Plugin for ResolveURL
    Copyright (c) 2024 pikdum

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import re

from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolverError, ResolveUrl
from six.moves import urllib_error, urllib_parse

logger = common.log_utils.Logger.get_logger(__name__)
# logger.disable()

AGENT = "ResolveURL for Kodi"
VERSION = common.addon_version
USER_AGENT = "{0}/{1}".format(AGENT, VERSION)


class TorBoxResolver(ResolveUrl):
    name = "TorBox"
    domains = ["*"]
    api_url = "https://api.torbox.app/v1/api"

    def __init__(self):
        self.hosters = None
        self.hosts = ["magnet"]
        self.headers = {
            "User-Agent": USER_AGENT,
            "Authorization": "Bearer %s" % self.__get_token(),
        }

    def __get(self, endpoint, query, empty=None):
        try:
            url = "{0}/{1}?{2}".format(
                self.api_url, endpoint, urllib_parse.urlencode(query)
            )
            result = self.net.http_GET(url, headers=self.headers).content
            if not result:
                return empty
            result = json.loads(result)
            if result.get("success"):
                return result.get("data")
            return empty
        except urllib_error.HTTPError as e:
            if e.code == 429:
                common.kodi.sleep(3000)
                return self.__get(endpoint, query, empty)
            return empty

    def __post(self, endpoint, data, empty=None):
        try:
            url = "{0}/{1}".format(self.api_url, endpoint)
            result = self.net.http_POST(url, form_data=data, headers=self.headers).content
            if not result:
                return empty
            result = json.loads(result)
            if result.get("success"):
                return result.get("data")
            return empty
        except urllib_error.HTTPError as e:
            if e.code == 429:
                common.kodi.sleep(3000)
                return self.__post(endpoint, data, empty)
            return empty

    def __create_torrent(self, magnet) -> dict | None:
        result = self.__post(
            "torrents/createtorrent", {"magnet": magnet}, {}
        )
        logger.log_warning("Create torrent: %s" % result)
        return result

    def __check_cache(self, btih) -> bool:
        result = self.__get(
            "torrents/checkcached",
            {"hash": btih, "format": "list", "list_files": False},
        )
        logger.log_warning("Check cache: %s" % result)
        return bool(result)

    def __check_ready(self, torrent_id) -> bool:
        result = self.__get(
            "torrents/mylist", {"id": torrent_id, "bypass_cache": True}, {}
        )
        return result.get("download_present", False)

    def __check_existing(self, btih) -> str | None:
        torrents = self.__get("torrents/mylist", {"bypass_cache": True}, [])
        for torrent in torrents:
            if torrent.get("hash") == btih:
                return torrent.get("id")
        return None

    def __download_link(self, torrent_id) -> str | None:
        return self.__get(
            "torrents/requestdl",
            {"torrent_id": torrent_id, "token": self.__get_token()},
        )

    def __get_token(self) -> str:
        return self.get_setting("apikey")

    def __get_hash(self, media_id) -> str | None:
        r = re.search("""magnet:.+?urn:([a-zA-Z0-9]+):([a-zA-Z0-9]+)""", media_id, re.I)
        if not r or len(r.groups()) < 2:
            return None
        return r.group(2)

    def get_media_url(
        self, host, media_id, cached_only=False, return_all=False
    ) -> str | None:
        # TODO: handle return_all
        # TODO: handle multiple files
        btih = self.__get_hash(media_id)
        logger.log_warning("BTIH: %s" % btih)
        cached = self.__check_cache(btih)
        logger.log_warning("Cached: %s" % cached)

        if not cached and cached_only:
            raise ResolverError("TorBox: {0}".format(i18n("cached_torrents_only")))

        # check if it's in your list
        torrent_id = self.__check_existing(btih)
        logger.log_warning("Torrent ID: %s" % torrent_id)
        if not torrent_id:
            # if not, add it
            torrent_id = self.__create_torrent(media_id).get("torrent_id")
            logger.log_warning("Torrent ID: %s" % torrent_id)

        # error adding torrent, abort
        if not torrent_id:
            logger.log_warning("Failed to add torrent - aborting.")
            return None

        # loop until it's ready
        # TODO: show progress dialog
        ready = cached
        while not ready:
            logger.log_warning("Waiting for torrent to be ready...")
            common.kodi.sleep(3000)
            ready = self.__check_ready(torrent_id)

        download_link = self.__download_link(torrent_id)
        logger.log_warning("Download link: %s" % download_link)
        return download_link

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return "torbox.app", url

    def valid_url(self, url, host):
        btih = self.__get_hash(url)
        return bool(btih)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append(
            '<setting id="%s_apikey" enable="eq(-1,true)" type="text" label="%s" default=""/>'
            % (cls.__name__, "API Key")
        )
        return xml

    @classmethod
    def isUniversal(self):
        return True
