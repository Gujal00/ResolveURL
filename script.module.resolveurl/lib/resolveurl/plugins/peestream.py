"""
    Plugin for ResolveURL
    Copyright (C) 2026 TempleLain

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
from six.moves import urllib_error
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class PeeStreamResolver(ResolveUrl):
    name = 'PeeStream'
    domains = ['peestream.com', 'peeplayer.com']
    pattern = r'(?://|\.)((?:peestream|peeplayer)\.com)/(?:v|e)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': 'https://peeplayer.com/'
        }
        try:
            html = self.net.http_GET(web_url, headers=headers).content
        except urllib_error.HTTPError:
            # removed files and unknown ids get a 404 with {"detail":"Video not found"}
            raise ResolverError('File Not Found or Removed')
        # the player builds its playlist in the browser, the cast button hands the same video
        # to the receiver as a server playlist made from these two values
        msg_id = re.search(r'var\s+MSG_ID\s*=\s*(\d+)', html)
        token = re.search(r'var\s+STOK\s*=\s*"([^"]+)"', html)
        if msg_id and token:
            src = 'https://peeplayer.com/m/{0}/master.m3u8?t={1}'.format(msg_id.group(1), token.group(1))
            return src + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        # the share page on peestream.com only frames this player page, both use the same id
        return self._default_get_url('peeplayer.com', media_id, template='https://{host}/e/{media_id}')
