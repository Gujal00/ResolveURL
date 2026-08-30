"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal

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

import binascii
import json
import re
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidSonicResolver(ResolveUrl):
    name = 'VidSonic'
    domains = ['vidsonic.net', 'vixeo.io']
    pattern = r'(?://|\.)((?:vidsonic|vixeo)\.(?:net|io))/(?:e|d)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': ref,
            'Origin': ref[:-1]
        }
        html = self.net.http_GET(web_url, headers=headers).content
        src = ''
        r = re.search(r"const\s*_0x1\s*=\s*'([^']+)", html)
        if r:
            src = r.group(1)
        else:
            # newer player builds carry the same reversed hex string in a
            # base64 encoded json blob on the player root element instead
            r = re.search(r'data-config="([^"]+)"', html)
            if r:
                blob = r.group(1)
                cfg = json.loads(helpers.b64decode(blob))
                src = cfg.get('source', '')
        if src:
            src = binascii.unhexlify(src.replace('|', '')).decode()[::-1]
            return src + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')
