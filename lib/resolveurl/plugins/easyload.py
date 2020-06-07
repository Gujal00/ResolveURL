"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
import json
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class EasyLoadResolver(ResolveUrl):
    name = "easyload"
    domains = ['easyload.io']
    pattern = r'(?://|\.)(easyload\.io)/e/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}

        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search('data="([^"]+)', html)
        if match:
            data = json.loads(match.group(1).replace('&quot;', '"'))
            src = data.get('streams').get('0').get('src')
            return self.easyload_decode(src, '15') + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')

    def easyload_decode(self, src, t):
        url = ''.join([chr(ord(src[i]) ^ ord(t[i % len(t)])) for i in range(len(src))])
        return url
