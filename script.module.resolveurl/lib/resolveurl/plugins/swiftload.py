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
from six.moves import urllib_parse
from binascii import unhexlify
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class SwiftLoadResolver(ResolveUrl):
    name = 'SwiftLoad'
    domains = ['swiftload.io']
    pattern = r'(?://|\.)(swiftload\.io)/(?:d|e|v)/([0-9a-zA-Z$:/.]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        if not referer:
            referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': referer}
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'''id="swhash"\s*value="([^"]+).+?src:\s*decrypt\('([^']+)''', html, re.DOTALL)
        if match:
            surl = self.swift_decode(match.group(2), match.group(1))
            return surl + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')

    @staticmethod
    def swift_decode(k, s):
        a = 0
        for x in k:
            a = a ^ ord(x)
        s = unhexlify(s)
        u = ''
        for c in s:
            u += chr((c if isinstance(c, int) else ord(c)) ^ a)
        return u
