"""
    Plugin for ResolveURL
    Copyright (C) 2021 shellc0de

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


class HexUploadResolver(ResolveUrl):
    name = 'HexUpload'
    domains = ['hexupload.net']
    pattern = r'(?://|\.)(hexupload\.net)/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'Origin': web_url.rsplit('/', 1)[0],
            'Referer': web_url,
            'User-Agent': common.RAND_UA
        }
        html = self.net.http_GET(web_url, headers=headers).content
        # Can be found on some mp4 embeds
        burl = re.search(r'b4aa\.buy\("([^"]+)', html)
        if burl:
            url = helpers.b64decode(burl.group(1))
            return url + helpers.append_headers(headers)

        payload = helpers.get_hidden(html)
        payload.update({'dataType': 'json', 'ajax': '1'})
        r = self.net.http_POST(headers['Origin'], form_data=payload, headers=headers)
        if 'text/html' not in r.get_headers(as_dict=True)['Content-Type']:
            url = json.loads(r.content).get('link')
            if url:
                url = helpers.b64decode(url)
                return url.replace(' ', '%20') + helpers.append_headers(headers)

        payload = {
            'op': 'download2',
            'id': media_id,
            'rand': '',
            'referer': web_url,
            'method_free': 'Free Download'
        }
        html = self.net.http_POST(web_url, form_data=payload, headers=headers).content
        url = re.search(r"ldl.ld\('([^']+)", html)
        if url:
            url = helpers.b64decode(url.group(1))
            return url.replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
