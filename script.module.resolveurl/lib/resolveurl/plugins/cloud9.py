"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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


class Cloud9Resolver(ResolveUrl):
    name = "Cloud9"
    domains = ["cloud9.to"]
    pattern = r'(?://|\.)(cloud9\.to)/embed/([0-9a-zA-Z-_]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Origin': 'https://{0}'.format(host)}
        html = self.net.http_GET(web_url, headers).content
        data = json.loads(html)
        sources = [(vid.get('height'), vid.get('file')) for vid in data.get('data', {}).get('sources', {})]
        if sources:
            sources.sort(key=lambda x: int(x[0]), reverse=True)
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://api.{host}/stream/{media_id}?cp=0')
