"""
    Plugin for ResolveUrl
    Copyright (C) 2020 cywteow

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

import base64
import json
import six
import re
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib.pyaes import AESModeOfOperationCBC, Encrypter, Decrypter
from six.moves import urllib_parse


class GoloadResolver(ResolveUrl):
    name = "goload"
    domains = ['goload.io']
    pattern = r'(?://|\.)(goload\.io)/(?:streaming\.php|embedplus)\?id=([a-zA-Z0-9-]+)'
    key1 = six.ensure_binary('54674138327930866480207815084989')
    key2 = six.ensure_binary('37911490979715163134003223491201')
    iv = six.ensure_binary('3134003223491201')

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = self.net.http_GET(web_url, headers=headers).content
        response = json.loads(response).get('data')
        if response:
            result = self._decrypt(response, self.key1)
            result = json.loads(result)
            str_url = result.get('source')[0].get('file') or result.get('source_bk')[0].get('file')
            if str_url:
                headers.pop('X-Requested-With')
                return str_url + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        id = self._encrypt(media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'X-Requested-With': 'XMLHttpRequest'
        }
        html = self.net.http_GET('https://{0}/streaming.php?id={1}'.format(host, media_id), headers=headers).content
        result = re.search(r'(?:<\s*?script[\s\S](?:.*)(?:data-name=\"episode\")[\s\S]*?(?:(?:data-value=[\'\"](.*?)[\'\"])(?:[\S\s]*?))?>)(?:[\s\S]*?)</script>', html)
        if result:
            params = self._decrypt(result.group(1), self.key2)

        return 'https://{0}/encrypt-ajax.php?id={1}&alias={2}'.format(host, id, params)

    def _encrypt(self, msg):
        encrypter = Encrypter(AESModeOfOperationCBC(self.key2, self.iv))
        ciphertext = encrypter.feed(msg)
        ciphertext += encrypter.feed()
        ciphertext = base64.b64encode(ciphertext)
        return six.ensure_str(ciphertext)

    def _decrypt(self, msg, key):
        ct = base64.b64decode(msg)
        decrypter = Decrypter(AESModeOfOperationCBC(key, self.iv))
        decrypted = decrypter.feed(ct)
        decrypted += decrypter.feed()
        return six.ensure_str(decrypted)