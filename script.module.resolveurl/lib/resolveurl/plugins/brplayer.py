"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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

from resolveurl.lib import helpers
import re
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class BRPlayerResolver(ResolveUrl):
    name = 'BRPlayer'
    domains = ['brplayer.site']
    pattern = r'(?://|\.)(watch\.brplayer\.site)/watch\?v=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'sniff\("[^"]+","([^"]+)","([^"]+)".+?],([^,]+)', html)
        if r:
            source = "https://{0}/m3u8/{1}/{2}/master.txt?s=1&cache={3}".format(
                host, r.group(1), r.group(2), r.group(3)
            )
            headers.update({'Referer': web_url})
            return source + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/watch?v={media_id}')
