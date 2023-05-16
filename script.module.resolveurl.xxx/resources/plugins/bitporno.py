"""
    Plugin for ResolveURL
    Copyright (C) 2018 gujal

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


class BitPornoResolver(ResolveUrl):
    name = 'bitporno'
    domains = ['bitporno.com', 'bitporno.to']
    pattern = r'(?://|\.)(bitporno\.(?:com|to))/(?:embed/|e/|v/|\?v=)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': 'https://www.{}/'.format(host), 'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        url = re.search(r'file:\s*"([^"]+)', html)
        if url:
            if not url.group(1).endswith('.m3u8'):
                return url.group(1) + helpers.append_headers(headers)
            surl = '{}{}'.format(web_url.rsplit('/', 1)[0], url.group(1)) if url.group(1).startswith('/') else url.group(1)
            return surl + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.bitporno.to/?v={media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
