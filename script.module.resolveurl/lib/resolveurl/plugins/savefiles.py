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


class SaveFilesResolver(ResolveUrl):
    name = 'SaveFiles'
    domains = ['savefiles.com', 'streamhls.to']
    pattern = r'(?://|\.)((?:savefiles|streamhls)\.' \
              r'(?:com|to))/(?:e/|v/)?([0-9a-zA-Z]+)'

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

        player_html = self.net.http_POST(dl_url, form_data=post_data, headers=headers).content
        s = re.search(r'''sources:\s*\[{\s*file\s*:\s*['"]([^'"]+)''', player_html)
        if s:
            stream_url = s.group(1) + helpers.append_headers(headers)
            if subs:
                subtitles = helpers.scrape_subtitles(player_html, web_url)
                return stream_url, subtitles
            return stream_url

        raise ResolverError("Unable to locate stream URL.")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
