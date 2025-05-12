"""
    Plugin for ResolveURL
    Copyright (c) 2025 gujal

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


class StreamUpResolver(ResolveUrl):
    name = 'StreamUp'
    domains = ['streamup.ws']
    pattern = r'(?://|\.)(streamup\.ws)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'fetch\(`([^=]+=)[^`]+`\)\.then', html)
        if r:
            headers.update({
                'Referer': 'https://{0}/'.format(host),
                'Origin': 'https://{0}'.format(host)
            })
            surl = r.group(1) + media_id
            sdata = json.loads(self.net.http_GET(surl, headers=headers).content)
            s = sdata.get('streaming_url')
            if s:
                return s + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
