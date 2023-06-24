"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de

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


class UploadRajaResolver(ResolveUrl):
    name = 'UploadRaja'
    domains = ['uploadraja.com']
    pattern = r'(?://|\.)(uploadraja\.com)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'Origin': web_url.rsplit('/', 1)[0],
            'Referer': web_url,
            'User-Agent': common.RAND_UA
        }
        payload = {
            'op': 'download2',
            'id': media_id,
            'rand': '',
            'referer': 'https://{}/'.format(host)
        }
        html = self.net.http_POST(web_url, headers=headers, form_data=payload).content
        source = re.search(r'href="([^"]+)"\s*class="download', html)
        if source:
            query = urllib_parse.parse_qsl(urllib_parse.urlparse(source.group(1)).query)
            src = query[1][1] if query else source.group(1)
            return src.replace(' ', '%20').replace('https:', 'http:') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
