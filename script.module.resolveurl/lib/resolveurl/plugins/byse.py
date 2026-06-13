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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
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
        'byselapuix.com', 'embedplaybyse.top', 'sb1254w9megshle.org'
    ]
    pattern = (
        r'(?://|\.)((?:filemoon|cinegrab|moonmov|kerapoxy|furher|1azayf9w|81u6xl9d|f16px|sb1254w9megshle|'
        r'smdfs40r|bf0skv|z1ekv717|l1afav|222i8x|8mhlloqo|96ar|xcoic|f51rm|c1z39|boosteradx|vepoin|'
        r'(?:embedplay)?byse(?:sayeveum|tayico|zejataos|koze|sukior|jikuar|fujedu|dikamoum|buho|wihe|lapuix)?)'
        r'\.(?:sx|top?|s?k?in|link|nl|wf|com|eu|art|pro|cc|xyz|org|fun|net|lol|online))'
        r'/(?:(?:e|d|download)/)?([0-9a-zA-Z]+)'
    )

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': ref,
            'Origin': ref[:-1]
        }
        details_url = '{0}api/videos/{1}/embed/details'.format(ref, media_id)
        details = self.net.http_GET(details_url, headers=headers).json
        embed_url = details.get('embed_frame_url')
        if embed_url:
            ref = urllib_parse.urljoin(embed_url, '/')
            headers.update({
                'Referer': ref,
                'Origin': ref[:-1],
                'X-Embed-Parent': web_url
            })

        settings_url = '{0}api/videos/{1}/embed/settings'.format(ref, media_id)
        settings = self.net.http_GET(settings_url, headers=headers).json

        if settings.get('captcha_required'):
            challenge_url = '{0}api/videos/access/challenge'.format(ref)
            challenge = self.net.http_POST(challenge_url, headers=headers, form_data={}).json

            attest_url = '{0}api/videos/access/attest'.format(ref)
            attest = self.net.http_POST(attest_url, headers=headers, form_data=self.wn(challenge), jdata=True).json
            fingerprint = {
                'token': attest['token'],
                'viewer_id': attest['viewer_id'],
                'device_id': attest['device_id'],
                'confidence': attest['confidence'],
            }

            captcha_url = '{0}api/videos/{1}/embed/captcha'.format(ref, media_id)
            captcha = self.net.http_POST(captcha_url, headers=headers, form_data={'fingerprint': fingerprint}, jdata=True).json
            solution = self.er(captcha['pow_nonce'], captcha['pow_difficulty'])
            if solution is None:
                raise ResolverError('Unable to solve captcha')

            verify_url = '{0}api/videos/{1}/embed/captcha/verify'.format(ref, media_id)
            post_data = {'pow_token': captcha['pow_token'], 'solution': solution, 'fingerprint': fingerprint}
            verify = self.net.http_POST(verify_url, headers=headers, form_data=post_data, jdata=True).json
            headers.update({'X-Captcha-Token': verify.get('token')})

            playback_url = '{0}api/videos/{1}/embed/playback'.format(ref, media_id)
            data = self.net.http_POST(playback_url, headers=headers, form_data={'fingerprint': fingerprint}, jdata=True).json
        else:
            playback_url = '{0}api/videos/{1}/embed/playback'.format(ref, media_id)
            data = self.net.http_POST(playback_url, headers=headers, form_data=self.fp(16, 0.6, 0.9), jdata=True).json

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
                return uri + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        redirect_domains = ['boosteradx.online', 'byse.sx']
        if host in redirect_domains:
            host = 'streamlyplayer.online'
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')

    @staticmethod
    def ft(e):
        return helpers.b64urldecode(e, binary=True)

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
        from random import uniform
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

    @staticmethod
    def wn(ch):
        from resolveurl.lib.ecdsa import SigningKey, NIST256p
        from hashlib import sha256
        sk = SigningKey.generate(curve=NIST256p, hashfunc=sha256)
        vk = sk.verifying_key.pubkey.point
        signature = sk.sign(ch.get('nonce').encode(), hashfunc=sha256)
        pub = {
            'crv': 'P-256', 'ext': True, 'key_ops': ['verify'], 'kty': 'EC',
            'x': helpers.b64urlencode(vk.x().to_bytes(32, 'big'), strip=True),
            'y': helpers.b64urlencode(vk.y().to_bytes(32, 'big'), strip=True),
        }
        sig = helpers.b64urlencode(signature, strip=True)
        return {
            'viewer_id': '',
            'device_id': '',
            'challenge_id': ch['challenge_id'],
            'nonce': ch['nonce'],
            'signature': sig,
            'public_key': pub,
            'client': {
                'user_agent': common.RAND_UA,
                'pixel_ratio': 1,
                'screen_width': 1366,
                'screen_height': 768,
                'color_depth': 24,
                'hardware_concurrency': 1,
                'touch_points': 0,
                'pointer_type': 'fine,hover'
            },
            'storage': {},
            'attributes': {'entropy': 'high'}
        }

    @staticmethod
    def re(t, e):
        m = 0xFFFFFFFF
        return (t << e | t >> (32 - e)) & m

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
        for r in range(len(t)):
            n = int(t[r])
            if n == 0:
                e += 32
                continue
            return e + (32 - n.bit_length())
        return e

    def er(self, t, e, r=20.0):
        import time
        if e <= 0:
            return '0'
        start = time.time()
        s = 0
        while True:
            for _ in range(1024):
                d = self.gr((t + ':' + str(s)).encode('ascii'))
                if self.wr(d) >= e:
                    return str(s)
                s += 1
            if time.time() - start > r:
                return None
