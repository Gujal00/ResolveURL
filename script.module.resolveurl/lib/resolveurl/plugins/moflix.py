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
    domains = [
        'moflix-stream.fans', 'boosteradx.online', 'mov18plus.cloud', 'newer.stream',
        'moviesapi.club', 'boosterx.stream', 'vidstreamnew.xyz', 'plyrxcdn.site',
        'boltx.stream', 'chillx.top', 'watchx.top', 'bestx.stream', 'playerx.stream',
        'vidstreaming.xyz', 'raretoonsindia.co'
    ]
    pattern = r'(?://|\.)((?:moflix-stream|boostera?d?x|mov18plus|newer|plyrxcdn|' \
              r'w1\.moviesapi|vidstream(?:new|ing)|(?:chill|watch|best|bolt|player)x)\.' \
              r'(?:fans|online|cloud|club|stream|xyz|top|site|co))/' \
              r'(?:d|v)/([0-9a-zA-Z$:/.-_]+)'

    def get_media_url(self, host, media_id, subs=False):
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': 'https://{0}/'.format(host)
        }
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
            headers.update({'Referer': referer})
        elif 'moviesapi' in host:
            headers.update({'Referer': 'https://moviesapi.club/'})
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'''(?:const|var|let|window\.)\s*\w*\s*=\s*'([^']+)''', html)
        if r:
            html2 = self.mf_decrypt(r.group(1), host)
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

    def mf_decrypt(self, edata, host):
        """
        (c) 2025 yogesh-hacker
        """
        # Func ID: YVD_2R
        import base64
        import binascii
        from hashlib import sha256
        import json
        import os
        import random
        import time
        from resolveurl.lib import pyaes

        def b36encode(num):
            chars = '0123456789abcdefghijklmnopqrstuvwxyz'
            if num == 0:
                return '0'
            result = ''
            while num > 0:
                num, i = divmod(num, 36)
                result = chars[i] + result
            return result

        def get_nonce():
            random_float = random.random()
            x = b36encode(int(str(random_float).split('.')[1]))
            z = b36encode(int(time.time() * 1000))
            return x + z

        def mod_exp(base, exp, mod):
            base = int(base)
            exp = int(exp)
            mod = int(mod)
            result = 1
            while exp > 0:
                if exp & 1:
                    result = (result * base) % mod
                base = (base * base) % mod
                exp >>= 1
            return result

        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': 'https://{0}/'.format(host)
        }
        dh_modulus = int("0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF", 16)
        client_private_key = int(binascii.hexlify(os.urandom(32)), 16) % dh_modulus
        client_public_key = mod_exp(2, client_private_key, dh_modulus)
        data = {
            "nonce": get_nonce(),
            "client_public": str(client_public_key)
        }
        resp = json.loads(self.net.http_POST('https://{0}/api-2/prepair-token.php'.format(host), form_data=data, headers=headers, jdata=True).content)
        shared_secret = mod_exp(resp.get('server_public'), client_private_key, dh_modulus)
        derived_key = sha256(str(shared_secret).encode()).digest()
        nonce = get_nonce()
        data = {
            "nonce": nonce,
            "pre_token": resp.get('pre_token'),
            "csrf_token": resp.get('csrf_token')
        }
        resp = json.loads(self.net.http_POST('https://{0}/api-2/create-token.php'.format(host), form_data=data, headers=headers, jdata=True).content)
        data.update({
            "token": resp.get('token'),
            "initial_nonce": nonce,
            "nonce": get_nonce(),
            "encrypted_data": edata
        })
        response = json.loads(self.net.http_POST('https://{0}/api-2/last-process.php'.format(host), form_data=data, headers=headers, jdata=True).content)
        decryptor = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(derived_key, base64.b64decode(response['temp_iv'])))
        actual_aes_key = decryptor.feed(base64.b64decode(response['encrypted_symmetric_key']))
        actual_aes_key += decryptor.feed()
        decryptor = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(actual_aes_key, base64.b64decode(response['iv'])))
        decrypted_payload = decryptor.feed(base64.b64decode(response['encrypted_result']))
        decrypted_payload += decryptor.feed()
        return decrypted_payload.decode('utf-8')
