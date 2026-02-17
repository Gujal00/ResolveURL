"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal, mrdini123

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class BunnyCDNResolver(ResolveUrl):
    name = 'BunnyCDN'
    domains = ['netcinepy.lat', 'rrrv.lol']
    pattern = r'(?://|\.)((?:netcinepy|rrrv)\.(?:lat|lol))/(.*)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': ref,
            'Origin': ref[:-1]
        }
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'<a\s*href="([^"]+)"\s*class="btn">', html)
        if r:
            url = r.group(1)
            if not url.startswith('http'):
                url = urllib_parse.urljoin(web_url, url)
            html = self.net.http_GET(url, headers=headers).content
            s = re.search(r'<source.+?src="([^"]+)', html)
            if s:
                src = s.group(1)
                if not src.startswith('http'):
                    src = urllib_parse.urljoin(web_url, src)
                return src + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/{media_id}')
