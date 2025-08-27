"""
    Plugin for ResolveUrl
    Copyright (C) 2024 Ghb3245
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
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class WecimaResolver(ResolveUrl):
    name = 'Wecima'
    domains = ['wecima.show', 'wecima.movie', 'wecima.stream', 'wecima.watch',
               'vbn1.t4ce4ma.shop', 'vbn2.t4ce4ma.shop', 'vbn3.t4ce4ma.shop', 'wecima.film',
               'wecima.tube', 'wecima.video', 'wecima.tv']
    pattern = r'(?://|\.)((?:wecima|vbn[123]\.t4ce4ma)\.(?:show|movie|stream|watch|shop|film|tube|video|tv))/run/([^\n]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        if not referer:
            referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer,
                   'X-Requested-With': 'XMLHttpRequest'}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = re.search(r'source\s*src="(?P<url>[^"]+)', html)
        if sources:
            headers.pop('X-Requested-With')
            return urllib_parse.quote(sources.group(1), ':/?=&') + helpers.append_headers(headers)
        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/run/{media_id}')
