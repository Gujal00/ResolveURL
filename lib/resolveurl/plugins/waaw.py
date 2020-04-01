'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import urllib
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class WaawResolver(ResolveUrl):
    name = "waaw"
    domains = ["waaw.tv", "hqq.watch", "netu.tv", "hqq.tv", "waaw1.tv"]
    pattern = r"(?://|\.)((?:waaw1?|netu|hqq)\.(?:tv|watch))/(?:watch_video\.php\?v|.+?vid)=([a-zA-Z0-9]+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'x-requested-with': 'XMLHttpRequest'}
        params = {'ver': '0',
                  'secure': '0',
                  'adb': '0/',
                  'v': media_id,
                  'token': '',
                  'gt': '',
                  'wasmcheck': 1}
        rurl = "https://hqq.tv/player/get_md5.php?" + urllib.urlencode(params)
        r = self.net.http_HEAD(rurl, headers=headers)
        if r.get_url() != rurl:
            return r.get_url() + '.mp4.m3u8' + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id,
                                     template='http://hqq.tv/player/embed_player.php?vid={media_id}&autoplay=no')
