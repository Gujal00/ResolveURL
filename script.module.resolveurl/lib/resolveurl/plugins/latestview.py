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

import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class LatestViewResolver(ResolveUrl):
    name = 'LatestView'
    domains = ['latestview.co']
    pattern = r'(?://|\.)(latestview\.co)/video/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'X-Requested-With': 'XMLHttpRequest'}
        pdata = {'hash': media_id,
                 'r': 'https://{0}/'.format(host)}
        resp = json.loads(self.net.http_POST(web_url, form_data=pdata, headers=headers).content)
        str_url = resp.get('videoSource')
        if str_url:
            headers.pop('X-Requested-With')
            return str_url + helpers.append_headers(headers)
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}&do=getVideo')
