"""
    Plugin for ResolveUrl
    Copyright (C) 2019  script.module.resolveurl
    Copyright (C) 2022  shellc0de

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class GofileResolver(ResolveUrl):
    name = 'gofile'
    domains = ['gofile.io']
    pattern = r'(?://|\.)(gofile\.io)/(?:\?c=|d/)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        base_api = 'https://api.gofile.io'
        r = self.net.http_GET('{}/createAccount'.format(base_api), headers=headers)
        token = json.loads(r.content).get('data').get('token')
        if not token:
            raise ResolverError('Unable to retrieve token!')
        content_url = '{}/getContent?contentId={}&token={}&websiteToken=12345'.format(
            base_api, media_id, token
        )
        r = self.net.http_GET(content_url, headers=headers).content
        data = json.loads(r).get('data').get('contents')
        if not data:
            raise ResolverError('This file does not exist.')
        headers.update({'Cookie': 'accountToken={}'.format(token)})
        sources = [(data[x].get('size'), data[x].get('link')) for x in data]
        return helpers.pick_source(sources, False) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/d/{media_id}')
