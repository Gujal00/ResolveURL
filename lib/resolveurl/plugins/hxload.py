'''
    ResolveUrl site plugin
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

from lib import helpers
import re
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class HXLoadResolver(ResolveUrl):
    name = "hxload"
    domains = ["hxload.co", "hxload.io"]
    pattern = r'(?://|\.)(hxload\.(?:co|io))/(?:embed/|\?e=)?([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r">var\s*hxstring\s*=\s*'([^']+)", html)
        if r:
            secret = "\x55\x62\x64\x6e\x42\x63\x36\x79\x50\x64\x71\x37\x44\x6f\x4b\x6f\x58\x6a\x44\x51\x6c\x46\x71\x71\x30\x6f\x67\x4d\x49\x71\x75\x45\x36\x33\x6b\x75\x45\x71\x57\x4b\x35\x32\x47\x52\x35\x53\x54\x39\x48\x63\x43\x45\x7a\x69\x69\x6b\x49\x61\x67\x63\x4b\x63\x6f\x55\x59\x71\x65\x53\x70\x37"
            html = self.hx_decrypt(secret, r.group(1).decode('base64'))
        sources = helpers.scrape_sources(html)
        
        if sources:
            return helpers.pick_source(sources) + helpers.append_headers(headers)
        
        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://hxload.co/embed/{media_id}')
    
    def hx_decrypt(self, key, enc_text):
        a = range(256)
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
