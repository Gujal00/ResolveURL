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

import codecs
import re
import json
from resolveurl.lib.jscrypto import jscrypto
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class MoflixStreamResolver(ResolveUrl):
    name = 'MoflixStream'
    domains = ['moflix-stream.fans']
    pattern = r'(?://|\.)(moflix-stream\.fans)/(?:d|v)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'''Contents\s*=\s*'([^']+)''', html)
        if r:
            data = json.loads(r.group(1))
            ct = data.get('ct')
            salt = codecs.decode(data.get('s'), 'hex')
            dt = jscrypto.decode(ct, '1FHuaQhhcsKgpTRB', salt)
            r = re.search(r'file:\s*\\"([^"]+)', dt)
            if r:
                murl = r.group(1).replace('\\', '')
                headers.update({
                    'Referer': 'https://{0}/'.format(host),
                    'Origin': 'https://{0}'.format(host)
                })
                return murl + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}/')
