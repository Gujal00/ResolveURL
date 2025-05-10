"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class PoopHDResolver(ResolveUrl):
    name = 'PoopHD'
    domains = ['poophd.me', 'videy.ro']
    pattern = r'(?://|\.)((?:poophd|videy)\.(?:me|ro))/(?:e/|d/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        embed_url = self.get_eurl(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': urllib_parse.urljoin(web_url, '/')
        }
        html = self.net.http_GET(embed_url, headers=headers).content
        r = re.search(r'initializePlayer\(\)\s*{.+?"l",\s*"([^"]+)', html)
        if r:
            return urllib_parse.quote(r.group(1), '/:?=') + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://poophd.me/e/{media_id}')

    def get_eurl(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://poophd.video-src.com/vplayer?id={media_id}')
