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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolverError, ResolveUrl
from six.moves import urllib_error, urllib_parse

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

AGENT = "ResolveURL for Kodi"
VERSION = common.addon_version
USER_AGENT = "{0}/{1}".format(AGENT, VERSION)


class TorBoxResolver(ResolveUrl):
    name = "TorBox"
    domains = ["*"]
    api_url = "https://api.torbox.app/v1/api"

    def __init__(self):
        self.hosters = None
        self.hosts = ["magnet", "tb"]
        self.headers = {
            "User-Agent": USER_AGENT,
            "Authorization": "Bearer %s" % self.__get_token(),
        }

    def __api(self, endpoint, query=None, data=None, empty=None):
        try:
            if query:
                url = "{0}/{1}?{2}".format(
                    self.api_url, endpoint, urllib_parse.urlencode(query)
                )
                result = self.net.http_GET(url, headers=self.headers).content
            if data:
                url = "{0}/{1}".format(self.api_url, endpoint)
                result = self.net.http_POST(
                    url, form_data=data, headers=self.headers, timeout=90
                ).content
            if not result:
                return empty
            result = json.loads(result)
            if result.get("success"):
                return result.get("data")
            return empty
        except urllib_error.HTTPError as e:
            if e.code == 429:
                common.kodi.sleep(1500)
                return self.__api(endpoint, query, data, empty)
            return empty

    def __get(self, endpoint, query, empty=None):
        return self.__api(endpoint, query=query, empty=empty)

    def __post(self, endpoint, data, empty=None):
        return self.__api(endpoint, data=data, empty=empty)

    def __create_torrent(self, magnet):
        result = self.__post("torrents/createtorrent", {"magnet": magnet}, {})
        return result

    def __check_cache(self, btih):
        result = self.__get(
            "torrents/checkcached",
            {"hash": btih, "format": "list", "list_files": False},
        )
        return bool(result)

    def __get_info(self, torrent_id):
        result = self.__get(
            "torrents/mylist", {"id": torrent_id, "bypass_cache": True}, {}
        )
        return result

    def __check_existing(self, btih):
        torrents = self.__get("torrents/mylist", {"bypass_cache": True}, [])
        for torrent in torrents:
            if torrent.get("hash") == btih:
                return (torrent.get("id"), torrent.get("name"))
        return (None, None)

    def __download_link(self, torrent_id, file_id):
        return self.__get(
            "torrents/requestdl",
            {"torrent_id": torrent_id, "file_id": file_id, "token": self.__get_token()},
        )

    def __get_token(self):
        return self.get_setting("apikey")

    def __get_hash(self, media_id):
        r = re.search("""magnet:.+?urn:([a-zA-Z0-9]+):([a-zA-Z0-9]+)""", media_id, re.I)
        if not r or len(r.groups()) < 2:
            return None
        return r.group(2)

    # hacky workaround to get return_all working
    # we prefix with tb:$file_id| to indicate which file to download
    # then handle it when re-resolving
    def __get_file_id(self, media_id):
        r = re.search(r"""tb:(\d*)\|(magnet:.*)""", media_id, re.I)
        if not r or len(r.groups()) < 2:
            return (None, media_id)
        return (int(r.group(1)), r.group(2))

    def get_media_url(self, host, media_id, cached_only=False, return_all=False):
        with common.kodi.ProgressDialog("ResolveURL TorBox") as d:
            (file_id, media_id) = self.__get_file_id(media_id)
            btih = self.__get_hash(media_id)
            d.update(0, line2="Checking cache...")
            cached = self.__check_cache(btih)

            cached_only = self.get_setting("cached_only") == "true" or cached_only
            if not cached and cached_only:
                raise ResolverError("TorBox: {0}".format(i18n("cached_torrents_only")))

            d.update(0, line2="Checking list...")
            (torrent_id, torrent_name) = self.__check_existing(btih)
            if not torrent_id:
                d.update(0, line2="Not in list, adding...")
                torrent = self.__create_torrent(media_id)
                torrent_id = torrent.get("torrent_id")

            if d.is_canceled():
                raise ResolverError("Cancelled by user")

            d.update(0, line1=torrent_name)

            if not torrent_id:
                raise ResolverError("Errror adding torrent")

            ready = cached
            while not ready:
                info = self.__get_info(torrent_id)
                torrent_name = info.get("name")
                ready = info.get("download_present", False)
                if ready:
                    break
                progress = int(info.get("progress", 0) * 100)
                state = "State: %s" % info.get("download_state")
                eta = "ETA: %ss" % info.get("eta")
                d.update(progress, line1=torrent_name, line2=state, line3=eta)
                if d.is_canceled():
                    raise ResolverError("Cancelled by user")
                common.kodi.sleep(1500)

        files = self.__get_info(torrent_id).get("files", [])

        if return_all:
            links = [
                {
                    "name": f.get("short_name"),
                    "link": "tb:%s|%s" % (f.get("id"), media_id),
                }
                for f in files
            ]
            return links

        # allow user to pick if multiple files
        if len(files) > 1 and file_id is None:
            links = [[f.get("short_name"), f.get("id")] for f in files]
            links.sort(key=lambda x: x[1])
            file_id = helpers.pick_source(links, auto_pick=False)
        else:
            file_id = 0

        download_link = self.__download_link(torrent_id, file_id)
        return download_link

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return "torbox.app", url

    def valid_url(self, url, host):
        (file_id, media_id) = self.__get_file_id(url)
        btih = self.__get_hash(media_id)
        # only supporting torrents through this plugin for now
        return bool(btih) and self.get_setting("torrents") == "true"

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append(
            '<setting id="%s_torrents" type="bool" label="%s" default="true"/>'
            % (cls.__name__, i18n("torrents"))
        )
        xml.append(
            '<setting id="%s_cached_only" enable="eq(-1,true)" type="bool" label="%s" default="false" />'
            % (cls.__name__, i18n("cached_only"))
        )
        xml.append(
            '<setting id="%s_apikey" enable="eq(-3,true)" type="text" label="%s" default=""/>'
            % (cls.__name__, "API Key")
        )
        return xml

    @classmethod
    def isUniversal(cls):
        return True

    @classmethod
    def _is_enabled(cls):
        return (
            cls.get_setting("enabled") == "true"
            and cls.get_setting("torrents") == "true"
            and cls.get_setting("apikey")
        )
