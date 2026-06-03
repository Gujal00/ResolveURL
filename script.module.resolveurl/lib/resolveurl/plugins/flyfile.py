"""
    Plugin for ResolveURL
    Copyright (C) 2026 icarok99

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

import json
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class FlyFileResolver(ResolveUrl):
    name = 'FlyFile'
    domains = ['flyfile.app']
    pattern = r'(?://|\.)(flyfile\.app)/embed/([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = 'https://{0}/'.format(host)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': ref,
            'Origin': ref[:-1]
        }
        resp = self.net.http_GET(web_url, headers=headers).content
        data = json.loads(resp)

        if data.get('url') and data.get('token'):
            stream_url = '{0}/hls/{1}/master.m3u8'.format(
                data['url'].rstrip('/'),
                data['token']
            )
            return stream_url + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://api.{host}/api/streaming/assign/{media_id}')
