"""
    Plugin for ResolveUrl
    Copyright (C) 2022 cywteow

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

import json
import six
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib.pyaes import AESModeOfOperationCBC, Encrypter, Decrypter
from six.moves import urllib_parse


class DembedResolver(ResolveUrl):
    name = "dembed2"
    domains = ['dembed2.com', 'asianplay.net', 'asianplay.pro', 'asianstream.pro', 'asianhdplay.net',
               'asianhdplay.pro', 'asianhd1.com']
    pattern = r'(?://|\.)((?:dembed2|asian(?:hd\d*)?(?:play|stream)?)\.(?:com|net|pro))/' \
              r'(?:streaming\.php|embedplus)\?id=([a-zA-Z0-9-]+)'
    key = six.ensure_binary('93422192433952489752342908585752')
    iv = six.ensure_binary('9262859232435825')

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = self.net.http_GET(web_url, headers=headers).content
        response = json.loads(response).get('data')
        if response:
            result = self._decrypt(response)
            result = json.loads(result)
            str_url = ''
            if len(result.get('source')) > 0:
                str_url = result.get('source')[0].get('file')
            if not str_url and len(result.get('source_bk')) > 0:
                str_url = result.get('source_bk')[0].get('file')
            if str_url:
                headers.pop('X-Requested-With')
                return str_url + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        params = {
            'op': '1',
            'refer': 'none',
            'id': self._encrypt(media_id),
            'alias': media_id
        }
        return 'https://{0}/encrypt-ajax.php?{1}'.format(host, urllib_parse.urlencode(params))

    def _encrypt(self, msg):
        encrypter = Encrypter(AESModeOfOperationCBC(self.key, self.iv))
        ciphertext = encrypter.feed(msg)
        ciphertext += encrypter.feed()
        ciphertext = helpers.b64encode(ciphertext)
        return ciphertext

    def _decrypt(self, msg):
        ct = helpers.b64decode(msg, binary=True)
        decrypter = Decrypter(AESModeOfOperationCBC(self.key, self.iv))
        decrypted = decrypter.feed(ct)
        decrypted += decrypter.feed()
        return six.ensure_str(decrypted)
