"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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
import re
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class ADramasResolver(ResolveUrl):
    name = 'ADramas'
    domains = ['vb.adramas.se']
    pattern = r'(?://|\.)(vb\.adramas\.se)/v/([0-9a-zA-Z-]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'var\s*VB_TOKEN\s*=\s*"([^"]+)', html)
        if r:
            headers.update({
                'Referer': 'https://{0}/'.format(host),
                'Origin': 'https://{0}'.format(host),
                'X-Requested-With': 'XMLHttpRequest'
            })
            data = {
                'VB_TOKEN': r.group(1),
                'VB_ID': media_id,
                'VB_NAME': 1
            }
            surl = 'https://{0}/v/p'.format(host)
            res = self.net.http_POST(surl, data, headers).content
            res = json.loads(res[1:])[-1]
            res = [helpers.b64decode(x.get('u')) for x in res if 'hls' in x.get('s').lower()]
            res = [x for x in res if '.m3u8' in x]
            if res:
                headers.pop('X-Requested-With')
                return res[0] + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}.html')
