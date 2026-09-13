"""
    Plugin for ResolveURL
    Copyright (C) 2026

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

from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidBasicLiveResolver(ResolveUrl):
    name = 'VidBasicLive'
    domains = ['vidbasic.live']
    pattern = r'(?://|\.)(vidbasic\.live)/stream/(?:[a-zA-Z0-9-]+/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        root = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': root,
            'Origin': root[:-1],
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = self.net.http_GET(web_url, headers=headers).json
        murl = data.get('sources', {}).get('file')
        if murl:
            headers.pop('X-Requested-With')
            return murl + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/stream/getSources?id={media_id}')
