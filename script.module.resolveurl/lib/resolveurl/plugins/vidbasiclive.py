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

from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidBasicLiveResolver(ResolveUrl):
    name = 'VidBasicLive'
    # vidbasic.live is NOT the same backend as vidbasic.top/vidb.top (see vidbasic.py):
    # embed path is /stream/{type}/{id} rather than /embed/{id}, and the id in the
    # url IS the realid the player uses - no need to fetch the embed page first.
    # /stream/getSources?id={id} returns plain JSON (no AES/crypto layer - confirmed
    # live), and the CDN file host requires Referer/Origin: vidbasic.live or it 403s.
    domains = ['vidbasic.live']
    pattern = r'(?://|\.)(vidbasic\.live)/stream/(?:[a-zA-Z0-9-]+/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        root = 'https://{0}/'.format(host)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': root,
            'Origin': root[:-1],
            'X-Requested-With': 'XMLHttpRequest',
        }
        sources_url = '{0}stream/getSources?id={1}'.format(root, media_id)
        data = self.net.http_GET(sources_url, headers=headers).json
        murl = data.get('sources', {}).get('file')
        if murl:
            headers.pop('X-Requested-With')
            return murl + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/stream/s-1/{media_id}')
