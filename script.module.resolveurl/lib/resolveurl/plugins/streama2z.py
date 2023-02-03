"""
    Plugin for ResolveURL
    Copyright (C) 2023 shellc0de

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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class Streama2zResolver(ResolveUrl):
    name = 'Streama2z'
    domains = ['streama2z.com', 'streama2z.xyz']
    pattern = r'(?://|\.)(streama2z\.(?:com|xyz))/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        rurl = 'https://streama2z.xyz/'
        headers = {
            'Origin': rurl[:-1],
            'Referer': rurl,
            'User-Agent': common.RAND_UA
        }
        payload = {
            'op': 'embed',
            'streama2z': '1',
            'id': media_id,
            'file_code': media_id,
            'referer': rurl
        }
        html = self.net.http_POST(web_url, form_data=payload, headers=headers).content
        html += helpers.get_packed_data(html)
        source = re.search(r'''sources:\s*\[{\s*src:\s*["']([^"']+)''', html)
        if source:
            return source.group(1) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://streama2z.com/embed-{media_id}.html')
