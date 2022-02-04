"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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

import re
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class HClipsResolver(ResolveUrl):
    name = 'hclips'
    domains = ['hclips.com']
    pattern = r'(?://|\.)(hclips\.com)/((?:videos|embed)/[\w\-]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.RAND_UA}
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content

        if media_id.startswith('embed/'):
            web_url = re.search(r'''link:\s*["']([^"']+)''', html).groups()[0]
            html = self.net.http_GET(web_url, headers=headers).content

        sources = re.findall(r'''['"]?file['"]?:\s*['"]([^'"]+).+?['"]?type['"]?:\s*['"]([^'"]+)''', html)
        if sources:
            sources = [(i[1], i[0]) for i in sources]
            return self.net.http_GET(helpers.pick_source(sources), headers=headers).get_url() + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
