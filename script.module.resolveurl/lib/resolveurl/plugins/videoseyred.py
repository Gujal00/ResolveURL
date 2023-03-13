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
import json
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VideoSeyredResolver(ResolveUrl):
    name = 'VideoSeyred'
    domains = ['videoseyred.in']
    pattern = r'(?://|\.)(videoseyred\.in)/(?:embed/|watch/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        headers.update({'Referer': web_url})

        match = re.search(r"playlistUrl='([^']+)", html)
        if match:
            web_url = 'https://{0}{1}'.format(host, match.group(1))
            html2 = self.net.http_GET(web_url, headers=headers).content
            r = json.loads(html2)[0].get('sources', None)
            if r:
                html = self.net.http_GET(r[0].get('file'), headers=headers).content
                sources = re.findall(r'RESOLUTION=\d+x(?P<label>[\d]+).*\n(?!#)(?P<url>[^\n]+)', html, re.I)
                if sources:
                    return helpers.pick_source(helpers.sort_sources_list(
                        sources)).replace('https:', 'http:') + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/embed/{media_id}')
