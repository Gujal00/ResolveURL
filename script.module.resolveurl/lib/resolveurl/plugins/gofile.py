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

import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class GoFileResolver(ResolveUrl):
    name = 'GoFile'
    domains = ['gofile.io']
    pattern = r'(?://|\.)(gofile\.io)/(?:\?c=|d/)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Origin': 'https://{0}'.format(host),
            'Referer': 'https://{0}/'.format(host)
        }
        base_api = 'https://api.gofile.io'
        r = self.net.http_POST('{}/accounts'.format(base_api), form_data="{}", headers=headers)
        token = json.loads(r.content).get('data', {}).get('token')
        if not token:
            raise ResolverError('Unable to retrieve token!')

        headers.update({
            'Authorization': 'Bearer ' + token,
            'x-website-token': self.__generateWT(token),
            'x-bl': 'en-US'
        })
        content_url = '{}/contents/{}?page=1'.format(base_api, media_id)
        r = self.net.http_GET(content_url, headers=headers).content
        data = json.loads(r).get('data').get('children')
        if data:
            headers = {
                'User-Agent': common.FF_USER_AGENT,
                'Referer': 'https://{0}/'.format(host),
                'Cookie': 'accountToken={}'.format(token)
            }
            sources = [(data[x].get('size'), data[x].get('link')) for x in data]
            return helpers.pick_source(sources, False) + helpers.append_headers(headers)

        raise ResolverError('File does not exist.')

    @staticmethod
    def __generateWT(tok):
        import math
        import time
        import hashlib
        rtime = math.floor(time.time() / 14400)
        wtok = '{0}::en-US::{1}::{2}::5d4f7g8sd45fsd'.format(common.FF_USER_AGENT, tok, rtime)
        return hashlib.sha256(wtok.encode('latin-1')).hexdigest()
