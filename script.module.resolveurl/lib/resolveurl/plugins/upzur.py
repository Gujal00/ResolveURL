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
import binascii
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class UpZurResolver(ResolveUrl):
    name = 'UpZur'
    domains = ['upzur.com']
    pattern = r'(?://|\.)(upzur\.com)/(?:embed-)?([a-zA-Z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'var\s*\w+\s*=\s*\["(.+?)"\]', html)
        if r:
            src = r.group(1).replace('","', '').replace('\\x', '')
            src = binascii.unhexlify(src).decode()[::-1]
            s = re.search(r'<source\s*src="([^"]+)', src)
            if s:
                rurl = 'https://{}/'.format(host)
                headers.update({'Origin': rurl[:-1], 'Referer': rurl, 'verifypeer': 'false'})
                return s.group(1) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
