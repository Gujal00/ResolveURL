"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class LoadXResolver(ResolveUrl):
    name = 'LoadX'
    domains = ['loadx.ws']
    pattern = r'(?://|\.)(loadx\.ws)/video/([a-f0-9]*)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        referer = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': referer,
            'Origin': referer[:-1],
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {'r': '', 'hash': media_id}
        response = self.net.http_POST(web_url, headers=headers, form_data=data).content
        src = json.loads(response).get('videoSource')
        if src:
            headers.pop('X-Requested-With')
            return src + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}&do=getVideo')
