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

from resolveurl.lib import helpers
import re
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidxGoResolver(ResolveUrl):
    name = 'VidxGo'
    domains = ['vidxgo.co']
    pattern = r'(?://|\.)(vidxgo\.co)/([0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': ref,
            'sec-fetch-dest': 'iframe'
        }
        html = self.net.http_GET(web_url, headers=headers).content
        scripts = re.findall(r'''<script>\s*\(function\(\){var\s*\w='([^']+)'[^']+'([^']+)''', html)
        decoded = [self.__vdecrypt(key, data) for key, data in scripts]
        sources = [re.findall(r'currentSrc\s*=\s*"([^"]+)', data)[0] for data in decoded if 'currentSrc' in data]
        if sources:
            strurl = sources[0].replace('\\', '')
            headers.update({
                'Origin': ref[:-1],
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site'
            })
            return strurl + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://v.{host}/{media_id}')

    @staticmethod
    def __vdecrypt(k, d):
        d = helpers.b64decode(d, binary=True)
        s = ''
        for i in range(len(d)):
            s += chr(d[i] ^ ord(k[i % len(k)]))
        return s
