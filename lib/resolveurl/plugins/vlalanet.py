"""
    Plugin for ResolveUrl
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

import re
import json
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common


class VlalaNetResolver(ResolveUrl):
    name = "vlalanet"
    domains = ["videoslala.net"]
    pattern = r'(?://|\.)(videoslala\.net)/embed/([^\n]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        html += helpers.get_packed_data(html)
        sources = re.search(r'sources:\s*(\[[^]]+])', html)
        if sources:
            sources = json.loads(sources.group(1))
            sources = [(x.get('label'), x.get('file')) for x in sources]
            source = helpers.pick_source(sorted(sources, reverse=True))
            return source + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
