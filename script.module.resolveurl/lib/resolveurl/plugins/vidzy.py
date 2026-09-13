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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidzyResolver(ResolveUrl):
    name = 'Vidzy'
    domains = ['vidzy.org', 'vidzy.cc']
    pattern = r'(?://|\.)(vidzy\.(?:org|cc))/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': urllib_parse.urljoin(web_url, '/')
        }
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'sources:\s*\[{src:\s*\(function\(s\).+?\}\)\("([^"]+)"\)', html, re.DOTALL)
        if r:
            source = self._decode_source(r.group(1), host)
            # a wrong key does not fail, the player just falls back to a decoy
            # playlist, so anything that is not a link is treated as no link
            if source.startswith('http'):
                return source + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')

    @staticmethod
    def _decode_source(blob, host):
        # the player keeps the source reversed, xored and base64 encoded, with
        # the xor key seeded from the hostname the page is served from, so the
        # seed has to be taken from the host instead of being hardcoded
        seed = 0
        for c in host:
            seed = (seed + ord(c)) & 255
        raw = helpers.b64decode(blob, binary=True)[::-1]
        source = ''
        for i in range(len(raw)):
            b = raw[i] if isinstance(raw[i], int) else ord(raw[i])
            source += chr(b ^ ((0x3d + i * 89 + seed) & 255))
        return source
