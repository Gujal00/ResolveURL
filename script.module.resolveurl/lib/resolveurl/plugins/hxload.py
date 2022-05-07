'''
    Plugin for ResolveURL
    Copyright (C) 2019 gujal

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
'''

from resolveurl.lib import helpers
import re
import base64
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class HXLoadResolver(ResolveUrl):
    name = "HXLoad"
    domains = ["hxload.to", "hxload.co", "hxload.io"]
    pattern = r'(?://|\.)(hxload\.(?:to|co|io))/(?:embed/|\?e=)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r"[>;]var\s*hxstring\s*=\s*'([^']+)", html)
        if r:
            b = "\x6b\x36\x73\x79\x7a\x6a\x61\x6a\x34\x6a\x7a\x61\x37\x32\x66\x31\x31\x33\x33\x30\x68\x6c\x76\x6e\x66\x6c\x6e\x62\x33\x68\x37\x79\x74\x68\x7a\x7a\x71\x66\x39\x6d\x37\x30\x6c\x79\x39\x7a\x7a\x76\x63\x33"
            html = base64.b64decode(r.group(1).encode('ascii'))
            html = self.hx_decrypt(b, html.decode('latin-1'))

        sources = helpers.scrape_sources(html)

        if sources:
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://hxload.to/embed/{media_id}')

    def hx_decrypt(self, key, enc_text):
        a = list(range(256))
        j = 0
        y = ''
        for i in range(256):
            j = (j + a[i] + ord(key[i % len(key)])) % 256
            s = a[i]
            a[i] = a[j]
            a[j] = s
        i = 0
        j = 0
        for k in range(len(enc_text)):
            i = (i + 1) % 256
            j = (j + a[i]) % 256
            s = a[i]
            a[i] = a[j]
            a[j] = s
            y += chr(ord(enc_text[k]) ^ a[(a[i] + a[j]) % 256])
        return y
