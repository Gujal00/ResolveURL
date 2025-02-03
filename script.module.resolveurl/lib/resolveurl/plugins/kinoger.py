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

import binascii
import json
from resolveurl.lib import helpers, pyaes
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class KinoGerResolver(ResolveUrl):
    name = 'KinoGer'
    domains = ['kinoger.re', 'shiid4u.upn.one', 'moflix.upns.xyz', 'player.upn.one']
    pattern = r'(?://|\.)((?:kinoger|(?:shiid4u|player)\.upn|moflix\.upns)\.(?:re|one|xyz))/#([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        edata = self.net.http_GET(web_url, headers=headers).content
        if edata:
            edata = binascii.unhexlify(edata[:-1])
            key = b'\x6b\x69\x65\x6d\x74\x69\x65\x6e\x6d\x75\x61\x39\x31\x31\x63\x61'
            iv = b'\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30\x6f\x69\x75\x79\x74\x72'
            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
            ddata = decrypter.feed(edata)
            ddata += decrypter.feed()
            ddata = ddata.decode('utf-8')
            ddata = json.loads(ddata)
            # r = ddata.get('cf')  # Plays with xbmc Player
            r = ddata.get('source')  # Plays with Inputstream Adaptive
            if r:
                headers.update({'Origin': referer[:-1]})
                return r + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/api/v1/video?id={media_id}')
