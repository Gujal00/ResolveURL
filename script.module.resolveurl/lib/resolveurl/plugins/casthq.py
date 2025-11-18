"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from six.moves import urllib_parse

from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class CastHQResolver(ResolveUrl):
    name = 'CastHQ'
    domains = ['casthq.to', 'vidspeeds.com', 'vidoba.org']
    pattern = r'(?://|\.)((?:casthq|vidspeeds|vidoba)\.(?:to|com|org))//?(?:e/|d/|embed-)?([0-9a-zA-Z=]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        dl_url = urllib_parse.urljoin(web_url, '/dl')
        post_data = {
            'op': 'embed',
            'file_code': media_id,
            'auto': '0'
        }
        headers = {
            "User-Agent": common.RAND_UA,
            "Referer": ref,
            "Origin": ref[:-1]
        }

        html = self.net.http_POST(dl_url, form_data=post_data, headers=headers).content
        html += helpers.get_packed_data(html)
        s = re.search(r'''sources:\s*\[{\s*file\s*:\s*['"]([^'"]+)''', html)
        if s:
            url = s.group(1) + helpers.append_headers(headers)
            if subs:
                subtitles = helpers.scrape_subtitles(html, web_url)
                return url, subtitles
            return url

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
