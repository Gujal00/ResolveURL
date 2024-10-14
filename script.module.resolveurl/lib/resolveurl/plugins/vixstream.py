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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VixStreamResolver(ResolveUrl):
    name = 'VixStream'
    domains = ['vixstream.co']
    pattern = r'(?://|\.)(vixstream\.co)/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.IOS_USER_AGENT,
                   'Referer': 'https://{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'var\s*_[0-9a-f]+\s*=\s*"([^"]+)', html)
        if r:
            res = self.decode_vix(r.group(1))
            su = re.search(r'sources:\s*\[{file:"([^"]+)', res)
            if su:
                src = helpers.get_redirect_url(su.group(1), headers)
                return src + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')

    @staticmethod
    def decode_vix(ct):
        key = '_0x3e68eb'
        s = ''
        ct = helpers.b64decode(ct, True)
        for x in range(len(ct)):
            s += chr((ct[x] if isinstance(ct[x], int) else ord(ct[x])) ^ ord(key[x % len(key)]))
        return s
