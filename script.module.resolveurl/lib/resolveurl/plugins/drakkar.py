"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal

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

from ast import literal_eval
import binascii
import hashlib
import json
import random
import re
import time
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.lib import pyaes
from resolveurl.resolver import ResolveUrl, ResolverError


class DrakkarResolver(ResolveUrl):
    name = 'Drakkar'
    domains = ['drakkar.st']
    pattern = r'(?://|\.)(drakkar\.st)/v/([0-9a-zA-Z-_]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(
            r"\(function\(\){\s*(var.+?)\s*var\s*_cr.+?_ept\s*=\s*'([^']+).+?_ws\s*=\s*'([^']+)",
            html, re.DOTALL
        )
        html = ''
        if r:
            _ts = int(time.time() * 1000)
            common.kodi.sleep(1500)
            if 'fromCharCode' in r.group(1):
                s = re.findall(r'=\s*(\[[^;]+)', r.group(1))
                if len(s) == 2:
                    _cr = self._xd(literal_eval(s[0]), literal_eval(s[1]))
                else:
                    t = int(r.group(1)[:-2].split(']')[-1])
                    _cr = ''
                    for i in literal_eval(s[0]):
                        _cr += chr(i + t)
            else:
                s = re.findall(r"=((?:atob\()?'[^']+)", r.group(1))
                if 'atob(' in s[0]:
                    _cr = helpers.b64decode(s[0].split("'")[-1]) + helpers.b64decode(s[1].split("'")[-1])
                else:
                    _cr = s[0].split("'")[-1][::-1] + s[1].split("'")[-1][::-1]
            data = {
                'cr': _cr,
                'pt': self._xd(r.group(2), _cr),
                'wc': self._wc(r.group(3), _cr),
                '_ts2': int(time.time() * 1000) - random.randint(100, 500),
                "bs": {
                    "ts": _ts,
                    "sw": 1280,
                    "sh": 720,
                    "plt": "",
                    "tz": 240,
                    "lang": "en-US",
                    "pl": "",
                    "ct": 4,
                    "dm": 24,
                    "td": 0,
                    "cv": 1,
                    "wg": 1
                }
            }
            ref = urllib_parse.urljoin(web_url, '/')
            headers.update({'Referer': ref, 'Origin': ref[:-1]})
            res = self.net.http_POST(web_url + '/stream', form_data=data, headers=headers, jdata=True).json
            if all([res.get('s'), res.get('d'), res.get('x')]):
                payload = self._dec(res.get('d'), res.get('v'), res.get('p1'), res.get('p2'), res.get('p3'), res.get('p4'), res.get('x'), _cr)
                if payload:
                    data = json.loads(payload)
                    if data.get('encrypted_player_data') and data.get('encrypted_player_data').get('ct'):
                        epd = data.get('encrypted_player_data')
                        html = self._decsimple(epd.get('ct'), epd.get('iv'), epd.get('k1'), epd.get('k2'), epd.get('k3'), epd.get('k4'))
                    elif data.get('processed_template'):
                        html = data.get('processed_template')
        if html:
            r = re.search(r"videoSrc:\s*'([^']+)", html)
            if r:
                url = r.group(1) + helpers.append_headers(headers)
                if subs:
                    subtitles = {}
                    s = re.search(r"subtitles:\s*(\[.+?]),", html)
                    if s:
                        s = json.loads(s.group(1))
                        subtitles = {x.get('lang'): x.get('src') for x in s}
                    return url, subtitles
                return url

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/v/{media_id}')

    @staticmethod
    def _xd(enc, key):
        r = ''
        for i in range(len(enc)):
            if isinstance(enc[i], int):
                r += chr(enc[i] ^ key[i % len(key)])
            else:
                r += format(int(enc[i], 16) ^ int(key[i % len(key)], 16), 'x')
        return r

    @staticmethod
    def _wc(seed, ch):
        return hashlib.sha256((seed + ch).encode('utf-8')).hexdigest()[:16]

    @staticmethod
    def _dec(d, iv, p1, p2, p3, p4, iphash, cr):
        try:
            key = hashlib.sha256((p1 + p2 + p3 + p4 + cr + iphash).encode()).digest()
            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, binascii.unhexlify(iv)))
            decrypted = decrypter.feed(helpers.b64decode(d, binary=True))
            decrypted += decrypter.feed()
            return decrypted.decode()
        except:
            return None

    @staticmethod
    def _decsimple(d, iv, p1, p2, p3, p4):
        key = binascii.unhexlify(p1 + p2 + p3 + p4)
        if len(key) not in [16, 24, 32]:
            return None
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, binascii.unhexlify(iv)))
        decrypted = decrypter.feed(helpers.b64decode(d, binary=True))
        decrypted += decrypter.feed()
        return decrypted.decode()
