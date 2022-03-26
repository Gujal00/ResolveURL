"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamLareResolver(ResolveUrl):
    name = "streamlare"
    domains = ["streamlare.com"]
    pattern = r'(?://|\.)(streamlare\.com)/(?:e|v)/([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        api_durl = 'https://streamlare.com/api/video/download/get'
        api_surl = 'https://streamlare.com/api/video/stream/get'
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url,
                   'X-Requested-With': 'XMLHttpRequest'}
        data = {'id': media_id}
        html = self.net.http_POST(api_surl, headers=headers, form_data=data, jdata=True).content
        source = json.loads(html).get('result', {}).get('file')
        if source:
            headers.pop('X-Requested-With')
            return source + helpers.append_headers(headers)
        else:
            html = self.net.http_POST(api_durl, headers=headers, form_data=data, jdata=True).content
            source = json.loads(html).get('result', {}).get('Original', {}).get('url')
            if source:
                headers.pop('X-Requested-With')
                return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
