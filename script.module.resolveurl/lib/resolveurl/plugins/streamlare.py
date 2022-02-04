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
        api_url = 'https://streamlare.com/api/video/get'
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url,
                   'X-Requested-With': 'XMLHttpRequest'}
        data = {'id': media_id}
        html = self.net.http_POST(api_url, headers=headers, form_data=data, jdata=True).content
        items = json.loads(html).get('result')
        sources = [('540p' if item == 'Original' else item, items.get(item).get('src')) for item in items.keys()]
        if sources:
            headers.pop('X-Requested-With')
            sources.sort(key=lambda x: int(x[0][:-1]), reverse=True)
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
