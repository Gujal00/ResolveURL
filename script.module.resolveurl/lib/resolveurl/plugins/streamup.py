"""
    Plugin for ResolveURL
    Copyright (c) 2025 Peter

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


class StreamupResolver(ResolveUrl):
    name = 'Streamup'
    domains = ['streamup.ws']
    pattern = r'(?://|\.)(streamup\.ws)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = 'https://bestb.stream/data.php?filecode={0}'.format(media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://{0}/'.format(host),
                   'origin': 'https://{0}'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = json.loads(html)['streaming_url']
        if sources:
            return sources + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    
