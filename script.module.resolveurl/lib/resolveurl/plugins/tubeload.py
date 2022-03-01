"""
    Plugin for ResolveUrl
    Copyright (C) 2022 shellc0de

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
import base64
from resolveurl import common
from resolveurl.plugins.lib import helpers, jsunhunt
from resolveurl.resolver import ResolveUrl, ResolverError


class TubeloadResolver(ResolveUrl):
    name = 'tubeload'
    domains = ['tubeload.co']
    pattern = r'(?://|\.)(tubeload\.co)/(?:embed|e|f)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        rurl = 'https://{}/'.format(host)
        headers = {
            'Referer': rurl,
            'User-Agent': common.FF_USER_AGENT
        }
        html = self.net.http_GET(web_url, headers=headers).content
        if 'NOT FOUND' in html or 'Sorry' in html:
            raise ResolverError('File Removed')

        if jsunhunt.detect(html):
            html = re.findall('<head>(.*?)</head>', html, re.S)[0]
            html = jsunhunt.unhunt(html)

        source = re.search(r'var\s*adbbdddffbad\s*=\s*"([^"]+)', html)
        if source:
            headers.update({'Origin': rurl[:-1], 'verifypeer': 'false'})
            url = source.group(1).replace('MzY3Y2E4NTAzNmQ5NDkzN2FiNTQzZTBiNmI4YTIwYzg', '')
            url = url.replace('NjYxOWU2OTNmZWQ0M2I3ZTFhM2U4NTc4Y2NhZmY3NmM=', '')
            url = base64.b64decode(url).decode('utf-8')
            return url + helpers.append_headers(headers)

        raise ResolverError('File Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
