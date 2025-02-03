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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class MoflixStreamResolver(ResolveUrl):
    name = 'MoflixStream'
    domains = ['moflix-stream.fans', 'boosteradx.online', 'mov18plus.cloud', 'moviesapi.club', 'boosterx.stream']
    pattern = r'(?://|\.)((?:moflix-stream|boostera?d?x|mov18plus|w1\.moviesapi)\.(?:fans|online|cloud|club|stream))/' \
              r'(?:d|v)/([0-9a-zA-Z$:/.-_]+)'

    def get_media_url(self, host, media_id, subs=False):
        headers = {'User-Agent': common.RAND_UA}
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
            headers.update({'Referer': referer})
        elif 'moviesapi' in host:
            headers.update({'Referer': 'https://moviesapi.club/'})
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'''(?:Encrypted(?:_Content)?|Matrixs?)\s*=\s*'([^']+)''', html)
        if r:
            html2 = self.mf_decrypt(r.group(1), headers['User-Agent'])
            r = re.search(r'file"?:\s*"([^"]+)', html2)
            if r:
                murl = r.group(1)
                headers.update({
                    'Referer': 'https://{0}/'.format(host),
                    'Origin': 'https://{0}'.format(host)
                })
                stream_url = murl + helpers.append_headers(headers)
                if subs:
                    subtitles = helpers.scrape_subtitles(
                        html2,
                        web_url,
                        patterns=[r'''["']?\s*(?:file|src)\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)(?:[^}>\]]+)["']?\s*label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)["'],"kind":"captions"'''],
                        generic_patterns=False
                    )
                    if not subtitles:
                        s = re.search(r'subtitle"?:\s*"([^"]+)', html2)
                        if s:
                            subs = s.group(1).split(',')
                            subtitles = {x.split(']')[0][1:]: x.split(']')[1] for x in subs}
                    return stream_url, subtitles
                return stream_url

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}')

    @staticmethod
    def mf_decrypt_lut(data):
        """
        (c) 2024 MrDini123
        """
        import zlib
        lookup_table = {
            "!": "a",
            "@": "b",
            "#": "c",
            "$": "d",
            "%": "e",
            "^": "f",
            "&": "g",
            "*": "h",
            "(": "i",
            ")": "j",
        }
        data = helpers.b64decode(data, binary=True)
        s = zlib.decompress(bytes(int(bin(byte)[2:].zfill(8)[::-1], 2) for byte in data)).decode('latin-1')
        s = "".join(lookup_table.get(char, char) for char in s)
        return helpers.b64decode(s)

    @staticmethod
    def mf_decrypt(data, ua):
        """
        (c) 2025 MrDini123
        """
        from hashlib import sha256
        from resolveurl.lib import pyaes
        import six
        data = helpers.b64decode(data, binary=True)
        # v4.6
        key = sha256(six.b('Fvv0O(0ep+X,q-Z+')).digest()
        decryptor = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, data[:16]))
        ddata = decryptor.feed(data[16:])
        ddata += decryptor.feed()
        return ddata.decode('utf-8')
