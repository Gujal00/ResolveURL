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


class OverThumbsResolver(ResolveUrl):
    name = 'overthumbs'
    domains = ['overthumbs.com']
    pattern = r'(?://|\.)(overthumbs\.com)/galleries/([\w\-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        video_id = re.search(r"""playvideo\.php\?id=(\d+)""", html)
        if video_id:
            video_url = 'http://%s/jwplayer/playvideo.php?id=%s' % (host, video_id.group(1))
            headers.update({'Referer': web_url})
            _html = self.net.http_GET(video_url, headers=headers).content
            _html = helpers.get_packed_data(_html)
            sources = helpers.scrape_sources(_html, patterns=[r'''file:\s*["'](?P<url>http[^"']+)'''])
            if sources:
                return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/galleries/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
