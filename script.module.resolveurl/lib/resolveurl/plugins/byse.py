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
import time
import uuid
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.lib.aesgcm import python_aesgcm
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


# ──────────────────────────────────────────────────────────────────────
# Proof-of-Work hash (reverse-engineered from pow--*.js).
# Labelled "sha256-leading-zero-bits" but is a custom 512-word mixing hash.
# Input = nonce + ":" + counter ; find counter with >= difficulty leading
# zero bits over the 8x uint32 output. Token TTL is 1800s so a multi-second
# blocking solve is fine for a Kodi resolver.
# ──────────────────────────────────────────────────────────────────────
_MASK = 0xFFFFFFFF
_BE, _LT, _DR, _LR, _HR = 512, 511, 2, 2654435761, 2246822519


def _pow_hash(data):
    e0, e1, e2, e3 = 1779033703, 3144134277, 1013904242, 2773480762
    M = _MASK
    for b in data:
        e0 = (e0 + b) & M
        e0 = ((e0 << 7) | (e0 >> 25)) & M
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 16) | (x >> 16)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 12) | (x >> 20)) & M
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 8) | (x >> 24)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 7) | (x >> 25)) & M
    for _ in range(8):
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 16) | (x >> 16)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 12) | (x >> 20)) & M
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 8) | (x >> 24)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 7) | (x >> 25)) & M
    r = [0] * _BE
    for i in range(_BE):
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 16) | (x >> 16)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 12) | (x >> 20)) & M
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 8) | (x >> 24)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 7) | (x >> 25)) & M
        r[i] = (e0 ^ e2) & M
    for _ in range(_DR):
        for s in range(_BE):
            a = r[s] & _LT
            c = (r[s] + r[a]) & M
            c = ((c << 13) | (c >> 19)) & M
            c = (c ^ ((r[(s + 1) & _LT] * _LR) & M)) & M
            r[s] = c
            e0 = (e0 ^ c) & M
            e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 16) | (x >> 16)) & M
            e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 12) | (x >> 20)) & M
            e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 8) | (x >> 24)) & M
            e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 7) | (x >> 25)) & M
    n = [0] * 8
    o = _BE // 8
    for i in range(8):
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 16) | (x >> 16)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 12) | (x >> 20)) & M
        e0 = (e0 + e1) & M; x = e3 ^ e0; e3 = ((x << 8) | (x >> 24)) & M
        e2 = (e2 + e3) & M; x = e1 ^ e2; e1 = ((x << 7) | (x >> 25)) & M
        s = e0
        a = i * o
        for cc in range(o):
            d = r[a + cc]
            s = (s + d) & M
            s = ((s << 5) | (s >> 27)) & M
            s = (s ^ ((d * _HR) & M)) & M
        n[i] = (s ^ e2) & M
    return n


def _lz_bits(words):
    bits = 0
    for n in words:
        if n == 0:
            bits += 32
            continue
        c = 0
        m = 0x80000000
        while m and not (n & m):
            c += 1
            m >>= 1
        return bits + c
    return bits


def _solve_pow(nonce, difficulty, timeout=30.0):
    if difficulty <= 0:
        return '0'
    prefix = nonce + ':'
    start = time.time()
    s = 0
    while True:
        for _ in range(2048):
            if _lz_bits(_pow_hash((prefix + str(s)).encode('latin-1'))) >= difficulty:
                return str(s)
            s += 1
        if time.time() - start > timeout:
            return None


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
        'byselapuix.com', 'embedplaybyse.top'
    ]
    pattern = (
        r'(?://|\.)((?:filemoon|cinegrab|moonmov|kerapoxy|furher|1azayf9w|81u6xl9d|f16px|embedplaybyse|'
        r'smdfs40r|bf0skv|z1ekv717|l1afav|222i8x|8mhlloqo|96ar|xcoic|f51rm|c1z39|boosteradx|vepoin|'
        r'byse(?:sayeveum|tayico|zejataos|koze|sukior|jikuar|fujedu|dikamoum|buho|wihe|lapuix)?)'
        r'\.(?:sx|top?|s?k?in|link|nl|wf|com|eu|art|pro|cc|xyz|org|fun|net|lol|online))'
        r'/(?:(?:e|d|download)/)?([0-9a-zA-Z]+)'
    )

    def _post_json(self, url, payload, headers):
        # Serialize JSON ourselves (compact, no spaces) and send as raw body so
        # the request is byte-identical across platforms. Relying on jdata=True
        # serializes nested dicts inconsistently on Kodi-Android -> 400.
        body = json.dumps(payload, separators=(',', ':'))
        h = dict(headers)
        h['Content-Type'] = 'application/json'
        try:
            return self.net.http_POST(url, headers=h, form_data=body).content
        except TypeError:
            # some ResolveURL builds want the raw body via `data=`
            return self.net.http_POST(url, headers=h, data=body).content

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)              # embed page url
        ref = urllib_parse.urljoin(web_url, '/')
        embed_origin = ref[:-1]
        embed_host = urllib_parse.urlparse(web_url).netloc

        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': web_url,
            'Origin': embed_origin,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        }

        # 1) details → embed_frame_url gives the real API host + referer
        try:
            details = json.loads(self.net.http_GET(
                '{0}/api/videos/{1}/embed/details'.format(embed_origin, media_id),
                headers=headers).content)
            frame = details.get('embed_frame_url') or web_url
        except Exception:
            frame = web_url
        api_origin = urllib_parse.urljoin(frame, '/')[:-1]
        referer = frame

        api_headers = dict(headers)
        api_headers.update({
            'Origin': api_origin,
            'Referer': referer,
            'X-Embed-Origin': embed_host,
            'X-Embed-Referer': web_url,
            'X-Embed-Parent': web_url,
        })

        # 2) settings → captcha required?
        try:
            settings = json.loads(self.net.http_GET(
                '{0}/api/videos/{1}/embed/settings'.format(api_origin, media_id),
                headers=api_headers).content)
            captcha_required = bool(settings.get('captcha_required'))
        except Exception:
            captcha_required = True

        # 3) challenge
        challenge = json.loads(self._post_json(
            '{0}/api/videos/access/challenge'.format(api_origin), {}, api_headers))

        # 4) attest → real server-issued token + viewer/device ids
        attest = json.loads(self._post_json(
            '{0}/api/videos/access/attest'.format(api_origin),
            self._attest_payload(challenge), api_headers))
        fingerprint = {
            'token': attest['token'],
            'viewer_id': attest['viewer_id'],
            'device_id': attest['device_id'],
            'confidence': attest['confidence'],
        }

        cookie = 'byse_viewer_id={0}; byse_device_id={1}'.format(
            fingerprint['viewer_id'], fingerprint['device_id'])
        cookie_headers = dict(api_headers)
        cookie_headers['Cookie'] = cookie

        # 5+6) captcha PoW
        captcha_token = None
        if captcha_required:
            cap = json.loads(self._post_json(
                '{0}/api/videos/{1}/embed/captcha'.format(api_origin, media_id),
                {'fingerprint': fingerprint}, cookie_headers))
            solution = _solve_pow(cap['pow_nonce'], cap['pow_difficulty'])
            if solution is None:
                raise ResolverError('Byse: PoW solve timed out')
            verify = json.loads(self._post_json(
                '{0}/api/videos/{1}/embed/captcha/verify'.format(api_origin, media_id),
                {'pow_token': cap['pow_token'], 'solution': solution, 'fingerprint': fingerprint},
                cookie_headers))
            if verify.get('status') != 'ok' or not verify.get('token'):
                raise ResolverError('Byse: captcha verify failed')
            captcha_token = verify['token']

        # 7) playback → verify token rides in X-Captcha-Token header (not the body)
        playback_headers = dict(cookie_headers)
        if captcha_token:
            playback_headers['X-Captcha-Token'] = captcha_token

        html = json.loads(self._post_json(
            '{0}/api/videos/{1}/embed/playback'.format(api_origin, media_id),
            {'fingerprint': fingerprint}, playback_headers))

        # output headers for the stream
        out_headers = {
            'User-Agent': headers['User-Agent'],
            'Referer': referer,
            'Origin': api_origin,
        }

        # Case 1: plain sources
        sources = html.get('sources')
        if sources:
            sources = [(x.get('label'), x.get('url')) for x in sources]
            uri = helpers.pick_source(helpers.sort_sources_list(sources))
            if uri.startswith('/'):
                uri = urllib_parse.urljoin(web_url, uri)
            url = helpers.get_redirect_url(uri, headers=out_headers)
            return url + helpers.append_headers(out_headers)

        # Case 2: encrypted playback
        pd = html.get('playback')
        if pd:
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
                return uri + helpers.append_headers(out_headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        redirect_domains = ['boosteradx.online', 'byse.sx']
        if host in redirect_domains:
            host = 'streamlyplayer.online'
        # embed page URL (NOT /playback anymore — the new flow needs /embed/* APIs)
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')

    @staticmethod
    def ft(e):
        t = e.replace('-', '+').replace('_', '/')
        return helpers.b64decode(t, binary=True)

    def xn(self, e, v):
        if v:
            v = int(v)
            e = [e[v - 1], e[len(e) - v]]
        t = list(map(self.ft, e))
        return b''.join(t)

    def _attest_payload(self, challenge):
        # ECDSA P-256 attestation with raw r||s signature (WebCrypto-compatible)
        try:
            from Crypto.Hash import SHA256
            from Crypto.PublicKey import ECC
            from Crypto.Signature import DSS
            key = ECC.generate(curve='P-256')
            digest = SHA256.new(challenge['nonce'].encode())
            signature = DSS.new(key, 'fips-186-3', encoding='binary').sign(digest)
            pub = {
                'alg': 'ES256', 'crv': 'P-256', 'ext': True, 'key_ops': ['verify'], 'kty': 'EC',
                'x': helpers.b64urlencode(int(key.pointQ.x).to_bytes(32, 'big'), strip=True),
                'y': helpers.b64urlencode(int(key.pointQ.y).to_bytes(32, 'big'), strip=True),
            }
            sig = helpers.b64urlencode(signature, strip=True)
        except Exception:
            # fallback: empty signature (server may still accept low-confidence)
            pub = {'alg': 'ES256', 'crv': 'P-256', 'ext': True, 'key_ops': ['verify'], 'kty': 'EC', 'x': '', 'y': ''}
            sig = ''

        return {
            'viewer_id': '',
            'device_id': '',
            'challenge_id': challenge['challenge_id'],
            'nonce': challenge['nonce'],
            'signature': sig,
            'public_key': pub,
            'client': {
                'user_agent': common.RAND_UA,
                'pixel_ratio': 2,
                'screen_width': 1536,
                'screen_height': 960,
                'color_depth': 24,
                'languages': ['en-US', 'en'],
                'timezone': 'Europe/Rome',
                'hardware_concurrency': 8,
                'touch_points': 0,
                'pointer_type': 'fine,hover',
                'extra': {'vendor': '', 'appVersion': '5.0 (Windows)'},
            },
            'storage': {},
            'attributes': {'entropy': 'low'},
        }
