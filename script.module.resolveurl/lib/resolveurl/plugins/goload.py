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


class GoloadResolver(ResolveUrl):
    name = 'GoLoad'
    domains = ['goload.io', 'goload.pro', 'gogohd.net', 'streamani.net', 'gogo-play.net',
               'vidstreaming.io', 'gogohd.pro', 'gembedhd.com', 'playgo1.cc', 'anihdplay.com']
    pattern = r'(?://|\.)(' \
              r'(?:gogo-play|streamani|goload|gogohd|vidstreaming|gembedhd|playgo1|anihdplay)\.(?:io|pro|net|com|cc))/' \
              r'(?:streaming|embed(?:plus)?|ajax|load)(?:\.php)?\?id=([a-zA-Z0-9-]+)'
    keys = ['37911490979715163134003223491201', '54674138327930866480207815084989']
    iv = six.ensure_binary('3134003223491201')

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'crypto-js\.js.+?data-value="([^"]+)', html)
        if r:
            params = self._decrypt(r.group(1))
            eurl = 'https://{0}/encrypt-ajax.php?id={1}&alias={2}'.format(
                host, self._encrypt(media_id), params)
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            response = self.net.http_GET(eurl, headers=headers).content
            response = json.loads(response).get('data')
            if response:
                result = self._decrypt(response, 1)
                result = json.loads(result)
                str_url = ''
                if len(result.get('source')) > 0:
                    str_url = result.get('source')[0].get('file')
                if not str_url and len(result.get('source_bk')) > 0:
                    str_url = result.get('source_bk')[0].get('file')
                if str_url:
                    headers.pop('X-Requested-With')
                    headers.update({'Referer': 'https://{0}/'.format(host),
                                    'Origin': 'https://{0}'.format(host)})
                    return str_url + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/streaming.php?id={media_id}')

    def _encrypt(self, msg, keyid=0):
        key = six.ensure_binary(self.keys[keyid])
        encrypter = Encrypter(AESModeOfOperationCBC(key, self.iv))
        ciphertext = encrypter.feed(msg)
        ciphertext += encrypter.feed()
        ciphertext = base64.b64encode(ciphertext)
        return six.ensure_str(ciphertext)

    def _decrypt(self, msg, keyid=0):
        ct = base64.b64decode(msg)
        key = six.ensure_binary(self.keys[keyid])
        decrypter = Decrypter(AESModeOfOperationCBC(key, self.iv))
        decrypted = decrypter.feed(ct)
        decrypted += decrypter.feed()
        return six.ensure_str(decrypted)
