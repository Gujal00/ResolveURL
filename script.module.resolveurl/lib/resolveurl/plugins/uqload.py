"""
    Plugin for ResolveURL
    Copyright (C) 2019 gujal

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
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric
from resolveurl.lib import jsunpack


class UQLoadResolver(ResolveGeneric):
    name = 'UQLoad'
    domains = [
        'uqload.com', 'uqload.co', 'uqload.io', 'uqload.to',
        'uqload.ws', 'uqload.net', 'uqload.cx', 'uqload.bz',
        'uqload.org', 'uqload.is'
    ]
    pattern = r'(?://|\.)(uqload\.(?:[ict]om?|[iw]s|net|cx|bz|org))/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        if jsunpack.detect(html):
            html = jsunpack.unpack(html)

        match = re.search(
            r'sources\s*:\s*\[\s*\{\s*file\s*[:\s\'"]+(?P<url>https?://[^\'\"]+\.m3u8[^\'\"]*)',
            html
        )
        if match:
            return match.group('url')

        raise self.ResolveException('Could not locate stream URL on {0}'.format(web_url))

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://uqload.is/embed-{media_id}.html')