"""
    Plugin for ResolveURL
    Copyright (C) 2026 icarok99

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib import helpers


class VrraTopResolver(ResolveUrl):
    name = 'VrraTop'
    domains = ['vrra.top']
    pattern = r'(?://|\.)(vrra\.top)/(?:e|embed)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers, timeout=60).content
        r = re.search(r'var\s*HANDSHAKE\s*=\s*"([^"]+)', html)
        if r:
            headers.update({
                'Referer': ref,
                'Origin': ref[:-1],
                'X-Requested-With': 'XMLHttpRequest'
            })
            api_url = urllib_parse.urljoin(ref, '/api/manifest')
            payload = {'h': r.group(1)}
            resp = self.net.http_POST(api_url, form_data=payload, headers=headers, jdata=True, timeout=60).content
            data = json.loads(resp)
            if data and data.get('url'):
                headers.pop('X-Requested-With')
                return data['url'] + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
