"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from hashlib import sha256
from random import random, uniform
from six.moves import urllib_parse, urllib_error
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class ByseResolver(ResolveUrl):
    name = 'Byse'
    domains = [
        'f16px.com', 'bysesayeveum.com', 'bysetayico.com', 'bysevepoin.com', 'bysezejataos.com',
        'bysekoze.com', 'bysesukior.com', 'bysejikuar.com', 'bysefujedu.com', 'bysedikamoum.com',
        'bysebuho.com', "byse.sx", 'filemoon.sx', 'filemoon.to', 'filemoon.in', 'filemoon.link',
        'filemoon.wf', 'cinegrab.com', 'filemoon.eu', 'filemoon.art', 'moonmov.pro', '96ar.com',
        'kerapoxy.cc', 'furher.in', '1azayf9w.xyz', '81u6xl9d.xyz', 'smdfs40r.skin', 'c1z39.com',
        'bf0skv.org', 'z1ekv717.fun', 'l1afav.net', '222i8x.lol', '8mhlloqo.fun', 'f51rm.com',
        'xcoic.com', 'filemoon.nl', 'boosteradx.online', 'streamlyplayer.online', 'bysewihe.com',
        'byselapuix.com', 'embedplaybyse.top', 'sb1254w9megshle.org', 'streamlyplayero.online',
        'moflix-stream.link', 'bysezoxexe.com', 'klcams.com', 'mfw09.org', 'kinoger.re'
    ]
    pattern = (
        r'(?://|\.)((?:filemoon|cinegrab|moonmov|kerapoxy|furher|1azayf9w|81u6xl9d|f16px|sb1254w9megshle|klcams|mfw09|kinoger|'
        r'smdfs40r|bf0skv|z1ekv717|l1afav|222i8x|8mhlloqo|96ar|xcoic|f51rm|c1z39|boosteradx|streamlyplayero?|moflix-stream|'
        r'(?:embedplay)?byse(?:sayeveum|tayico|zejataos|koze|sukior|jikuar|fujedu|dikamoum|buho|wihe|lapuix|vepoin|zoxexe)?)'
        r'\.(?:sx|top?|s?k?in|link|nl|wf|com|eu|art|pro|cc|xyz|org|fun|net|lol|online|re))'
        r'/(?:(?:e|d|download)/)?([0-9a-zA-Z]+(?:\$\$.+)?)'
    )
    UA = 'Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-G5510 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/7.2 Chrome/59.0.3071.125 Mobile Safari/537.36'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': self.UA,
            'Referer': ref,
            'Origin': ref[:-1]
        }
        if referer:
            # embed-restricted videos: the player sends the embedding page along with every API call
            parent = urllib_parse.urlparse(referer).hostname or ''
            headers.update({
                'X-Embed-Origin': parent[4:] if parent.startswith('www.') else parent,
                'X-Embed-Referer': referer
            })
        embed = ''
        details_url = '{0}api/videos/{1}/details'.format(ref, media_id)
        try:
            details = self.net.http_GET(details_url, headers=headers).json
        except urllib_error.HTTPError as e:
            if e.code == 404:
                embed = 'embed/'
                details_url = '{0}api/videos/{1}/{2}details'.format(ref, media_id, embed)
                try:
                    details = self.net.http_GET(details_url, headers=headers).json
                except urllib_error.HTTPError:
                    raise ResolverError('Video Link Not Found')
            else:
                raise ResolverError('Video Link Not Found')
        embed_url = details.get('embed_frame_url')
        if embed_url:
            ref = urllib_parse.urljoin(embed_url, '/')
            headers.update({
                'X-Embed-Parent': web_url,
                'Referer': ref,
                'Origin': ref[:-1],
            })

        settings_url = '{0}api/videos/{1}/{2}settings'.format(ref, media_id, embed)
        settings = self.net.http_GET(settings_url, headers=headers).json

        if settings.get('captcha_required'):
            challenge_url = '{0}api/videos/access/challenge'.format(ref)
            challenge = self.net.http_POST(challenge_url, headers=headers, form_data={}).json

            attest_url = '{0}api/videos/access/attest'.format(ref)
            attest = self.net.http_POST(attest_url, headers=headers, form_data=self.wn(challenge), jdata=True, timeout=40).json
            fingerprint = {
                'token': attest['token'],
                'viewer_id': attest['viewer_id'],
                'device_id': attest['device_id'],
                'confidence': attest['confidence']
            }

            captcha_url = '{0}api/videos/{1}/{2}captcha'.format(ref, media_id, embed)
            captcha = self.net.http_POST(captcha_url, headers=headers, form_data={'fingerprint': fingerprint}, jdata=True, timeout=40).json
            solution = self.er(captcha['pow_nonce'], captcha['pow_difficulty'])
            if solution is None:
                raise ResolverError('Unable to solve captcha')

            verify_url = '{0}api/videos/{1}/{2}captcha/verify'.format(ref, media_id, embed)
            post_data = {'pow_token': captcha['pow_token'], 'solution': solution, 'fingerprint': fingerprint}
            verify = self.net.http_POST(verify_url, headers=headers, form_data=post_data, jdata=True, timeout=40).json
            headers.update({'X-Captcha-Token': verify.get('token')})

            playback_url = '{0}api/videos/{1}/{2}playback'.format(ref, media_id, embed)
            data = self.net.http_POST(playback_url, headers=headers, form_data={'fingerprint': fingerprint}, jdata=True, timeout=40).json
        else:
            playback_url = '{0}api/videos/{1}/{2}playback'.format(ref, media_id, embed)
            data = self.net.http_POST(playback_url, headers=headers, form_data=self.fp(16, 0.83, 0.94), jdata=True, timeout=40).json

        sources = data.get('sources')
        if sources:
            sources = [(x.get('label'), x.get('url')) for x in sources]
            uri = helpers.pick_source(helpers.sort_sources_list(sources))
            if uri.startswith('/'):
                uri = urllib_parse.urljoin(ref, uri)
            url = helpers.get_redirect_url(uri, headers=headers)
            return url + helpers.append_headers(headers)
        pd = data.get('playback')
        if pd:
            from resolveurl.lib.aesgcm import python_aesgcm
            iv = self.ft(pd.get('iv'))
            key = self.xn(pd.get('key_parts'), pd.get('version'))
            pl = self.ft(pd.get('payload'))
            cipher = python_aesgcm.new(key)
            ct = cipher.open(iv, pl)
            ct = json.loads(ct.decode('latin-1'))
            sources = ct.get('sources')
            if sources:
                sources = [(x.get('label'), x.get('url')) for x in sources]
                uri = helpers.pick_source(helpers.sort_sources_list(sources))
                if 'X-Embed-Parent' in headers.keys():
                    headers.pop('X-Embed-Parent')
                if 'X-Captcha-Token' in headers.keys():
                    headers.pop('X-Captcha-Token')
                if 'X-Embed-Origin' in headers.keys():
                    headers.pop('X-Embed-Origin')
                if 'X-Embed-Referer' in headers.keys():
                    headers.pop('X-Embed-Referer')
                return uri + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        redirect_domains = ['boosteradx.online', 'byse.sx', 'streamlyplayer.online']
        if host in redirect_domains:
            host = 'streamlyplayero.online'
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')

    @staticmethod
    def ft(e):
        return helpers.b64urldecode(e, binary=True)

    @staticmethod
    def fh(e):
        return helpers.b64urlencode(sha256(str(e).encode('ascii')).digest(), strip=True)

    def xn(self, e, v):
        if v:
            v = int(v)
            e = [e[v - 1], e[len(e) - v]]
        t = list(map(self.ft, e))
        return b''.join(t)

    @staticmethod
    def fp(x, y, z):
        from binascii import hexlify
        from hashlib import sha256
        from os import urandom
        from time import time
        v_id = hexlify(urandom(x)).decode()
        d_id = hexlify(urandom(x)).decode()
        ctime = int(time())
        t_data = {
            'viewer_id': v_id,
            'device_id': d_id,
            'confidence': round(uniform(y, z), 2),
            'iat': ctime,
            'exp': ctime + 600
        }
        t_bdata = helpers.b64urlencode(json.dumps(t_data), strip=True)
        t_sig = helpers.b64urlencode(sha256(t_bdata.encode()).digest(), strip=True)
        token = '{0}.{1}'.format(t_bdata, t_sig)
        t_data.update({'token': token})
        t_data.pop('iat')
        t_data.pop('exp')
        return {'fingerprint': t_data}

    def wn(self, ch):
        from resolveurl.lib.ecdsa import SigningKey, NIST256p
        sk = SigningKey.generate(curve=NIST256p, hashfunc=sha256)
        vk = sk.verifying_key.to_string()
        signature = sk.sign(ch.get('nonce').encode(), hashfunc=sha256)
        pub = {
            'crv': 'P-256', 'ext': True, 'key_ops': ['verify'], 'kty': 'EC',
            'x': helpers.b64urlencode(vk[:32], strip=True),
            'y': helpers.b64urlencode(vk[32:], strip=True)
        }
        sig = helpers.b64urlencode(signature, strip=True)
        r = random()
        return {
            'viewer_id': '',
            'device_id': '',
            'challenge_id': ch['challenge_id'],
            'nonce': ch['nonce'],
            'signature': sig,
            'public_key': pub,
            'client': {
                'user_agent': self.UA,
                'architecture': 'arm',
                'bitness': '32',
                'platform': 'Android',
                'platform_version': '6.0.1',
                'model': 'SM-G5510',
                'ua_full_version': '59.0.3071.125',
                'brand_full_versions': [
                    {
                        'brand': 'SamsungBrowser',
                        'version': '7.2'
                    }
                ],
                'pixel_ratio': 1,
                'screen_width': 1280,
                'screen_height': 720,
                'color_depth': 24,
                'languages': [
                    'en-US'
                ],
                'timezone': 'America/New_York',
                'hardware_concurrency': 4,
                'device_memory': 2,
                'touch_points': 1,
                'canvas_hash': self.fh(r),
                'audio_hash': self.fh(r + 1),
                'fonts_hash': self.fh(r + 3),
                'codecs_hash': self.fh(r + 4),
                'media_devices': 'ai1ao1vi4',
                'pointer_type': 'coarse',
                'extra': {
                    'vendor': 'Samsung',
                    'appVersion': '7.2'
                }
            },
            'storage': {},
            'attributes': {'entropy': 'high'}
        }

    @staticmethod
    def re(t, e):
        return ((t << e) | (t >> (32 - e))) & 0xFFFFFFFF

    def ye(self, t):
        m = 0xFFFFFFFF
        t[0] = (t[0] + t[1]) & m
        t[3] = self.re(t[3] ^ t[0], 16)
        t[2] = (t[2] + t[3]) & m
        t[1] = self.re(t[1] ^ t[2], 12)
        t[0] = (t[0] + t[1]) & m
        t[3] = self.re(t[3] ^ t[0], 8)
        t[2] = (t[2] + t[3]) & m
        t[1] = self.re(t[1] ^ t[2], 7)

    def gr(self, t):
        m = 0xFFFFFFFF
        e = [1779033703, 3144134277, 1013904242, 2773480762]
        be, lt, dr, lr, hr = 512, 511, 2, 2654435761, 2246822519
        for i in t:
            e[0] = (e[0] + i) & m
            e[0] = self.re(e[0], 7)
            self.ye(e)
        for _ in range(8):
            self.ye(e)
        r = [0] * be
        for i in range(be):
            self.ye(e)
            r[i] = (e[0] ^ e[2]) & m
        for i in range(dr):
            for s in range(be):
                a = r[s] & lt
                c = (r[s] + r[a]) & m
                c = self.re(c, 13)
                c = (c ^ ((r[(s + 1) & lt] * lr) & m)) & m
                r[s] = c
                e[0] = (e[0] ^ c) & m
                self.ye(e)
        n = [0] * 8
        o = int(be / 8)
        for i in range(8):
            self.ye(e)
            s = e[0]
            a = i * o
            for c in range(o):
                d = r[a + c]
                s = (s + d) & m
                s = self.re(s, 5)
                s = (s ^ ((d * hr) & m)) & m
            n[i] = (s ^ e[2]) & m
        return n

    @staticmethod
    def wr(t):
        e = 0
        for n in t:
            if n == 0:
                e += 32
                continue
            return e + (32 - n.bit_length())
        return e

    @staticmethod
    def qr(a, b, c, d, m):
        a = (a + b) & m
        x = d ^ a
        d = ((x << 16) | (x >> 16)) & m
        c = (c + d) & m
        x = b ^ c
        b = ((x << 12) | (x >> 20)) & m
        a = (a + b) & m
        x = d ^ a
        d = ((x << 8) | (x >> 24)) & m
        c = (c + d) & m
        x = b ^ c
        b = ((x << 7) | (x >> 25)) & m
        return a, b, c, d

    def er(self, t, e, r=45.0):
        import struct
        import sys
        import time
        from array import array
        from operator import itemgetter
        if e <= 0:
            return '0'
        if e > 32 or sys.byteorder != 'little' or not hasattr(int, 'from_bytes'):
            return self.es(t, e, r)
        # Same result as es() (the smallest s), but 64 attempts at a time: each attempt has its own
        # 64 bit field in one big integer, so every addition, xor, shift and multiplication below
        # works on all of them in one step. Only the lookup r[r[s] & 511] differs per field, it goes
        # through a flat array. With e <= 32 only the first output word decides.
        k, m = 64, 0xFFFFFFFF
        ones = sum(1 << (64 * j) for j in range(k))
        mm, im, nb = ones * m, ones * 511, 8 * k
        jo = sum(j << (64 * j) for j in range(k))
        hi = ((m << (32 - e)) & m) * ones
        q = struct.Struct('<%dQ' % k)
        a, b, c, d = 1779033703, 3144134277, 1013904242, 2773480762
        for i in bytearray((t + ':').encode('ascii')):
            a = self.re((a + i) & m, 7)
            a, b, c, d = self.qr(a, b, c, d, m)
        st = (a * ones, b * ones, c * ones, d * ones)
        start = time.time()
        s, n, nx = 0, 1, 10
        while True:
            cnt = min(k, nx - s)
            ds = [str(v) for v in range(s, s + cnt)]
            ds += [ds[-1]] * (k - cnt)
            a, b, c, d = st
            for p in range(n):
                a = (a + int.from_bytes(q.pack(*[ord(x[p]) for x in ds]), 'little')) & mm
                a = ((a << 7) | (a >> 25)) & mm
                a, b, c, d = self.qr(a, b, c, d, mm)
            for _ in range(8):
                a, b, c, d = self.qr(a, b, c, d, mm)
            rr = [0] * 512
            for i in range(512):
                a, b, c, d = self.qr(a, b, c, d, mm)
                rr[i] = a ^ c
            fl = array('Q')
            fl.frombytes(b''.join([v.to_bytes(nb, 'little') for v in rr]))
            fv = memoryview(fl)
            for _ in range(2):
                for i in range(512):
                    x = rr[i]
                    y = itemgetter(*q.unpack(((x & im) * k + jo).to_bytes(nb, 'little')))(fl)
                    y = (x + int.from_bytes(q.pack(*y), 'little')) & mm
                    y = ((y << 13) | (y >> 19)) & mm
                    y ^= (rr[(i + 1) & 511] * 2654435761) & mm
                    rr[i] = y
                    fv[i * k:i * k + k] = memoryview(y.to_bytes(nb, 'little')).cast('Q')
                    a, b, c, d = self.qr(a ^ y, b, c, d, mm)
            a, b, c, d = self.qr(a, b, c, d, mm)
            x = a
            for v in rr[:64]:
                x = (x + v) & mm
                x = ((x << 5) | (x >> 27)) & mm
                x ^= (v * 2246822519) & mm
            x = q.unpack(((x ^ c) & hi).to_bytes(nb, 'little'))
            for j in range(cnt):
                if not x[j]:
                    return str(s + j)
            s += cnt
            if s == nx:
                n, nx = n + 1, nx * 10
            if time.time() - start > r:
                return None

    def es(self, t, e, r):
        # one attempt at a time, the reference for er()
        import time
        start = time.time()
        s = 0
        t += ':'
        while True:
            for _ in range(1024):
                d = self.gr((t + str(s)).encode('ascii'))
                if self.wr(d) >= e:
                    return str(s)
                s += 1
            if time.time() - start > r:
                return None
