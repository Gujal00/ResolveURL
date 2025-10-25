"""
    Plugin for ResolveURL
    Copyright (C) 2024 mrdini123, gujal

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

import binascii
import json
import re
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VeevResolver(ResolveUrl):
    name = 'Veev'
    domains = ['veev.to', 'poophq.com', 'doods.to']
    pattern = r'(?://|\.)((?:veev|poophq|doods)\.(?:to|com))/(?:e|d)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT, 'Referer': web_url}
        r = self.net.http_GET(web_url, headers=headers)
        if r.get_url() != web_url:
            media_id = r.get_url().split('/')[-1]
        # Still dancing
        items = re.findall(r'''[\.\s'](?:fc|_vvto\[[^\]]*)(?:['\]]*)?\s*[:=]\s*['"]([^'"]+)''', r.content)
        if items:
            for f in items[::-1]:
                ch = veev_decode(f)
                if ch != f:
                    params = {
                        'op': 'player_api',
                        'cmd': 'gi',
                        'file_code': media_id,
                        'ch': ch,
                        'ie': 1
                    }
                    durl = urllib_parse.urljoin(web_url, '/dl') + '?' + urllib_parse.urlencode(params)
                    jresp = self.net.http_GET(durl, headers=headers).content
                    jresp = json.loads(jresp).get('file')
                    if jresp and jresp.get('file_status') == 'OK':
                        str_url = decode_url(veev_decode(jresp.get('dv')[0].get('s')), build_array(ch)[0])
                        return str_url + helpers.append_headers(headers)
                    raise ResolverError('Video removed')

            raise ResolverError('Unable to locate video')

        raise ResolverError('Video removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')


def veev_decode(etext):
    result = []
    lut = {}
    n = 256
    c = etext[0]
    result.append(c)
    for char in etext[1:]:
        code = ord(char)
        nc = char if code < 256 else lut.get(code, c + c[0])
        result.append(nc)
        lut[n] = c + nc[0]
        n += 1
        c = nc

    return ''.join(result)


def js_int(x):
    return int(x) if x.isdigit() else 0


def build_array(encoded_string):
    d = []
    c = list(encoded_string)
    count = js_int(c.pop(0))
    while count:
        current_array = []
        for _ in range(count):
            current_array.insert(0, js_int(c.pop(0)))
        d.append(current_array)
        count = js_int(c.pop(0))

    return d


def decode_url(etext, tarray):
    ds = etext
    for t in tarray:
        if t == 1:
            ds = ds[::-1]
        ds = binascii.unhexlify(ds).decode('utf8')
        ds = ds.replace('dXRmOA==', '')

    return ds
