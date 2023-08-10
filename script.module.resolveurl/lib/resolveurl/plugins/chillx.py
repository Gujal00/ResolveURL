"""
    Plugin for ResolveURL
    Copyright (C) 2022 gujal

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
import json
import codecs
import hashlib
from resolveurl.lib import helpers, pbkdf2, pyaes
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class ChillXResolver(ResolveUrl):
    name = 'ChillX'
    domains = ['chillx.top', 'watchx.top', 'bestx.stream']
    pattern = r'(?://|\.)((?:chill|watch|best)x\.(?:top|stream))/v/([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        html = self.net.http_GET(web_url, headers=headers).content
        edata = re.search(r"MasterJS\s*=\s*'([^']+)", html)
        if edata:
            edata = helpers.b64decode(edata.group(1))
            edata = json.loads(edata)
            key = '\x31\x31\x78\x26\x57\x35\x55\x42\x72\x63\x71\x6e\x24\x39\x59\x6c'
            ct = edata.get('ciphertext', False)
            salt = codecs.decode(edata.get('salt'), 'hex')
            iv = codecs.decode(edata.get('iv'), 'hex')
            secret = pbkdf2.PBKDF2(key, salt, 999, hashlib.sha512).read(32)
            decryptor = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(secret, iv))
            ddata = decryptor.feed(helpers.b64decode(ct, binary=True))
            ddata += decryptor.feed()
            ddata = ddata.decode('utf-8')
            r = re.search(r'sources:\s*\[{"file":"([^"]+)', ddata) \
                or re.search(r'"video_player",\s*file:\s*"([^"]+)', ddata)
            if r:
                headers.update({'Origin': referer[:-1], 'verifypeer': 'false'})
                return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}/')
