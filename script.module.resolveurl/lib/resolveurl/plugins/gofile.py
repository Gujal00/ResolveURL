"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de
                  2024 peter3344

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class GoFileResolver(ResolveUrl):
    name = 'GoFile'
    domains = ['gofile.io']
    pattern = r'(?://|\.)(gofile\.io)/(?:\?c=|d/)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Origin': 'https://{0}'.format(host),
                   'Referer': 'https://{0}/'.format(host)
                   }
        base_api = 'https://api.gofile.io'
        r = self.net.http_POST('{}/accounts'.format(base_api), form_data="{}", headers=headers)
        token = json.loads(r.content).get('data').get('token')
        if not token:
            raise ResolverError('Unable to retrieve token!')

        r = self.net.http_GET('https://{}/dist/js/alljs.js'.format(host), headers=headers).content
        wtoken = re.search(r'fetchData\s*=\s*{\s*wt:\s*"([^"]+)', r)
        if not wtoken:
            raise ResolverError('Unable to retrieve websiteToken!')

        headers.update({'Authorization': 'Bearer ' + token})
        content_url = '{}/contents/{}?wt={}&cache=true'.format(base_api, media_id, wtoken.group(1))
        r = self.net.http_GET(content_url, headers=headers).content
        data = json.loads(r).get('data').get('children')
        if data:
            headers.pop('Authorization')
            headers.update({'Cookie': 'accountToken={}'.format(token)})
            sources = [(data[x].get('size'), data[x].get('link')) for x in data]
            return helpers.pick_source(sources, False) + helpers.append_headers(headers)

        raise ResolverError('This file does not exist.')
