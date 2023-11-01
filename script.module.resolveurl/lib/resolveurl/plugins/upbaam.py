"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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


class UpBaamResolver(ResolveUrl):
    name = 'UpBaam'
    domains = ['upbaam.com', 'cdnupbom.com']
    pattern = r'(?://|\.)((?:upbaam|cdnupbom)\.com)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'Origin': 'https://{0}'.format(host),
            'Referer': web_url,
            'User-Agent': common.RAND_UA
        }
        payload = {
            'op': 'download2',
            'id': media_id,
            'rand': '',
            'referer': web_url
        }
        html = self.net.http_POST(web_url, form_data=payload, headers=headers).content
        url = re.search(r'id="direct_link".+?href="([^"]+)', html, re.DOTALL)
        if url:
            return url.group(1).replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
