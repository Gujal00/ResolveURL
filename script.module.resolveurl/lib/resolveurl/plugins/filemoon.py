"""
    Plugin for ResolveUrl
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
import json
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class FileMoonResolver(ResolveUrl):
    name = 'FileMoon'
    domains = ['filemoon.sx', 'filemoon.to']
    pattern = r'(?://|\.)(filemoon\.(?:sx|to))/(?:e|d)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        html = helpers.get_packed_data(html)
        r = re.search(r'''b:\s*'([^']+)',\s*file_code:\s*'([^']+)',\s*hash:\s*'([^']+)''', html)
        if r:
            url = 'https://{}/dl'.format(host)
            payload = {'b': r.group(1), 'file_code': r.group(2), 'hash': r.group(3)}
            headers.update({'Origin': url[:-3], 'Referer': url[:-2]})
            req = self.net.http_POST(url, form_data=payload, headers=headers)
            data = json.loads(req.content)[0]
            vfile = data.get('file')
            seed = data.get('seed')
            source = helpers.tear_decode(vfile, seed)
            if source:
                return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
