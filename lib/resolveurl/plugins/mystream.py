"""
    plugin for ResolveURL
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
"""

import re
from lib import aadecode
from lib import jjdecode
from resolveurl import common
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class MystreamResolver(ResolveUrl):
    name = "mystream"
    domains = ['mystream.la', 'mystream.to']
    pattern = r'(?://|\.)(my?stream\.(?:la|to|cloud|xyz))/(?:external|watch/)?([0-9a-zA-Z_]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if "unable to find the video" in html:
            raise ResolverError('The requested video was not found or may have been removed.')

        match = re.search(r'type="file".+?script>\s*([^<]+)', html, re.DOTALL)
        if match:
            aa_text = aadecode.decode(match.group(1).encode('utf8'))
            match = re.search(r"atob\('([^']+)", aa_text)
            if match:
                etext = match.group(1).decode("base64")
                secret = self.vv_secret(html)
                stream_url = self.vv_decrypt(secret, etext)
                return stream_url + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://embed.mystream.to/{media_id}')

    def vv_secret(self, page):
        jjtext = re.search("<script>([^<]+)", page)
        jjdecoded = jjdecode.JJDecoder(jjtext.group(1)).decode()
        parts = re.search(r"atob\('([^']+)", jjdecoded).group(1).decode("base64").split("|")
        hash_val = parts[1]
        var_sec = re.findall(r"<script>var[^=]+=\s*(.+?){if", page)[0]
        words = re.findall(r"'(?!get|set|]|\))([^']{10,})'", var_sec)
        words.sort(key=len)
        n, l, h = words
        domtable = {}
        for j in range(len(l)):
            for k in range(len(n)):
                domtable[l[j] + n[k]] = h[j + k]
        key = ""
        for i in range(0, len(hash_val), 2):
            key = key + domtable[hash_val[i] + hash_val[i + 1]]
        return key

    def vv_decrypt(self, key, enc_text):
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
