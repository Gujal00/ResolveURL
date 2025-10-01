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

import re
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class SibnetResolver(ResolveUrl):
    name = 'Sibnet'
    domains = ['sibnet.ru']
    pattern = r'(?://|\.)(sibnet\.ru)/(?:shell\.php\?videoid=|.*video)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://video.sibnet.ru/'}
        html = self.net.http_GET(web_url, headers=headers).content
        source = re.search(r'src:\s*"([^"]+)"', html)
        if source:
            relative_path = source.group(1)
            if not relative_path.startswith('/'):
                relative_path = '/' + relative_path

            stream_url = 'https://video.sibnet.ru' + relative_path
            return stream_url + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://video.{host}/shell.php?videoid={media_id}')
