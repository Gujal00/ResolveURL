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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class SpeedFilesResolver(ResolveUrl):
    name = 'SpeedFiles'
    domains = ['speedfiles.net']
    pattern = r'(?://|\.)(speedfiles\.net)/([a-f0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        ctvar = re.search(r''''load',function\(\).+?atob\(([^)]*)''', html)
        if ctvar:
            ct = re.search(r'''var\s*{0}\s*=\s*"([^"]+)'''.format(ctvar.group(1)), html)
            if ct:
                src = self.sfdecode(ct.group(1))
                headers.update({'Referer': 'https://{0}/'.format(host)})
                return src + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    def sfdecode(self, enc_text):
        import binascii
        s = helpers.b64decode(enc_text)
        s = helpers.b64decode(s.swapcase()[::-1])
        s = binascii.unhexlify(s[::-1])
        s = ''.join([chr((x if isinstance(x, int) else ord(x)) - 3) for x in s])
        url = helpers.b64decode(s.swapcase()[::-1])
        return url
