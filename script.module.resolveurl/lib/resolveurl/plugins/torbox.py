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

import re
from six.moves import urllib_parse, urllib_error
import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
# logger.disable()

AGENT = "ResolveURL for Kodi"
VERSION = common.addon_version
USER_AGENT = "{0}/{1}".format(AGENT, VERSION)
FORMATS = common.VIDEO_FORMATS

api_url = "https://api.torbox.app/v1/api"


class TorBoxResolver(ResolveUrl):
    name = "TorBox"
    domains = ["*"]

    def __init__(self):
        self.hosters = None
        self.hosts = ["magnet"]
        self.headers = {
            "User-Agent": USER_AGENT,
            "Authorization": "Bearer %s" % self.__get_token(),
        }

    def __create_torrent(self, magnet) -> dict | None:
        logger.log_warning("Creating torrent for magnet: %s" % magnet)
        url = "{0}/torrents/createtorrent".format(api_url)
        data = {"magnet": magnet, "as_queued": True}
        result = self.net.http_POST(url, form_data=data, headers=self.headers).content
        # TODO: if this throws 400 error, probably free tier rate limit
        # is free tier worth handling specially?
        if not result:
            return None
        result = json.loads(result)
        if result.get("success"):
            return result.get("data")
        return None

    def __check_cache(self, hash) -> bool:
        logger.log_warning("Checking cache for hash: %s" % hash)
        url = "{0}/torrents/checkcached?hash={1}&format=list&list_files=false".format(
            api_url, hash
        )
        result = self.net.http_GET(url, headers=self.headers).content
        if not result:
            return False
        result = json.loads(result)
        return bool(result.get("data"))

    def __check_ready(self, torrent_id) -> bool:
        # TODO: handle rate limiting (429 status)
        return True
        logger.log_warning("Checking if torrent is ready: %s" % torrent_id)
        url = "{0}/torrents/mylist?id={1}&bypass_cache=true".format(api_url, torrent_id)
        result = self.net.http_GET(url, headers=self.headers).content
        if not result:
            return False
        result = json.loads(result)
        if result.get("success"):
            return result.get("data").get("download_present")
        return False

    def __check_existing(self, hash) -> str | None:
        logger.log_warning("Checking existing torrent for hash: %s" % hash)
        url = "{0}/torrents/mylist?bypass_cache=true".format(api_url)
        result = self.net.http_GET(url, headers=self.headers).content
        if not result:
            return None
        result = json.loads(result)
        if result.get("success"):
            torrents = result.get("data")
            for torrent in torrents:
                if torrent.get("hash") == hash:
                    return torrent.get("id")
        return None

    def __download_link(self, torrent_id) -> str | None:
        logger.log_warning("Getting download link for torrent: %s" % torrent_id)
        url = "{0}/torrents/requestdl?torrent_id={1}&token={2}".format(
            api_url, torrent_id, self.__get_token()
        )
        logger.log_warning("URL: %s" % url)
        result = self.net.http_GET(url, headers=self.headers).content
        logger.log_warning("Result: %s" % result)
        if not result:
            return None
        result = json.loads(result)
        if result.get("success"):
            return result.get("data")
        return None

    def __get_token(self) -> str:
        return self.get_setting("apikey")

    def get_media_url(
        self, host, media_id, cached_only=False, return_all=False
    ) -> str | None:
        logger.log_warning("Media ID: %s" % media_id)
        # TODO: handle return_all
        r = re.search("""magnet:.+?urn:([a-zA-Z0-9]+):([a-zA-Z0-9]+)""", media_id, re.I)
        if not r:
            return None
        hash = r.group(2)
        cached = self.__check_cache(hash)
        if not cached and cached_only:
            raise ResolverError("TorBox: {0}".format(i18n("cached_torrents_only")))
        # TODO: this is a workaround to bypass rate limit on create torrent, even if already added
        torrent_id = self.__check_existing(hash)
        if not torrent_id:
            torrent_id = self.__create_torrent(media_id).get("torrent_id")
        # loop until check_ready is Tru
        # TODO: show progress dialog
        while not self.__check_ready(torrent_id):
            logger.log_debug("TorBox: Torrent not ready")
            common.kodi.sleep(5000)
        download_link = self.__download_link(torrent_id)
        logger.log_warning("Download link: %s" % download_link)
        return download_link

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return "torbox.app", url

    def valid_url(self, url, host):
        return True

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append(
            '<setting id="%s_apikey" enable="eq(-1,true)" type="text" label="%s" option="hidden" default=""/>'
            % (cls.__name__, "API Key")
        )
        return xml

    @classmethod
    def isUniversal(self):
        return True
