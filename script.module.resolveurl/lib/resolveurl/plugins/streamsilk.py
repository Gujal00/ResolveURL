"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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
from resolveurl.lib import helpers, jsunhunt
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamSilkResolver(ResolveUrl):
    name = 'StreamSilk'
    domains = ['streamsilk.com']
    pattern = r'(?://|\.)(streamsilk\.com)/(?:d|p|v)/([0-9a-zA-Z$:/.]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        if referer:
            headers.update({'Referer': referer})
        html = self.net.http_GET(web_url, headers=headers).content
        if jsunhunt.detect(html):
            html = jsunhunt.unhunt(html)
        r = re.search(r'urlPlay\s*=\s*"([^"]+)', html)
        if r:
            headers.update({
                'Referer': 'https://{0}/'.format(host),
                'Origin': 'https://{0}'.format(host)
            })
            return r.group(1).strip() + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/p/{media_id}')
