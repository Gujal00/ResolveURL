"""
    Plugin for ResolveURL
    Copyright (C) 2020  gujal

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
import base64
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VoeResolver(ResolveUrl):
    name = "voe"
    domains = ["voe.sx"]
    pattern = r'(?://|\.)(voe\.sx)/(?:e/)?([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'uttf0\((\[[^)]+)', html)
        if r:
            r = eval(r.group(1))
            r = base64.b64decode(''.join(r)[::-1].encode('utf8')).decode('utf8')
            return r + helpers.append_headers(headers)

        sources = helpers.scrape_sources(
            html,
            patterns=[r'''hls":\s*"(?P<url>[^"]+)",\s*"video_height":\s*(?P<label>[^,]+)'''],
            generic_patterns=False
        )
        if sources:
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
