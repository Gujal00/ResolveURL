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
import uuid
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.lib.aesgcm import python_aesgcm
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

try:
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import ECC
    from Crypto.Signature import DSS
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


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
        'byselapuix.com'
    ]
    pattern = (
        r'(?://|\.)((?:filemoon|cinegrab|moonmov|kerapoxy|furher|1azayf9w|81u6xl9d|f16px|'
        r'smdfs40r|bf0skv|z1ekv717|l1afav|222i8x|8mhlloqo|96ar|xcoic|f51rm|c1z39|boosteradx|'
        r'byse(?:sayeveum|tayico|vepoin|zejataos|koze|sukior|jikuar|fujedu|dikamoum|buho|wihe|lapuix)?)'
        r'\.(?:sx|to|s?k?in|link|nl|wf|com|eu|art|pro|cc|xyz|org|fun|net|lol|online))'
        r'/(?:(?:e|d|download)/)?([0-9a-zA-Z]+)'
    )

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        embed_url = 'https://{0}/e/{1}'.format(host, media_id)
        origin = 'https://{0}'.format(host)

        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': embed_url,
            'Origin': origin,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Embed-Origin': host,
            'X-Embed-Referer': embed_url,
            'X-Embed-Parent': embed_url,
        }

        # Try attested fingerprint first, fall back to simple
        try:
            fp = self.fp_attested(host, embed_url, headers)
        except Exception:
            fp = self.fp_simple(16, 0.6, 0.9)

        html = self.net.http_POST(web_url, headers=headers, form_data=fp, jdata=True).content
        html = json.loads(html)

        # Case 1: plain sources
        sources = html.get('sources')
        if sources:
            sources = [(x.get('label'), x.get('url')) for x in sources]
            uri = helpers.pick_source(helpers.sort_sources_list(sources))
            if uri.startswith('/'):
                uri = urllib_parse.urljoin(web_url, uri)
            url = helpers.get_redirect_url(uri, headers=headers)
            return url + helpers.append_headers(headers)

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
                return uri + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        redirect_domains = ['boosteradx.online', 'byse.sx']
        if host in redirect_domains:
            host = 'streamlyplayer.online'
        return self._default_get_url(host, media_id, 'https://{host}/api/videos/{media_id}/embed/playback')

    @staticmethod
    def ft(e):
        t = e.replace('-', '+').replace('_', '/')
        return helpers.b64decode(t, binary=True)

    @staticmethod
    def xn(parts, version):
        """Derive 32-byte AES key: parts[v-1] + parts[n-v]"""
        v = int(version)
        n = len(parts)  # always 30
        def dec(s):
            s = s.replace('-', '+').replace('_', '/')
            return helpers.b64decode(s, binary=True)
        return dec(parts[v - 1]) + dec(parts[n - v])

    def fp_attested(self, host, embed_url, headers):
        """EC P-256 attested fingerprint (full challenge/attest flow)."""
        if not HAS_CRYPTO:
            raise ImportError('pycryptodome not available')

        origin = 'https://{0}'.format(host)
        challenge_url = '{0}/api/videos/access/challenge'.format(origin)
        challenge = json.loads(
            self.net.http_POST(challenge_url, headers=headers, form_data={}, jdata=True).content
        )

        key = ECC.generate(curve='P-256')
        digest = SHA256.new(challenge['nonce'].encode())
        signature = DSS.new(key, 'fips-186-3', encoding='binary').sign(digest)

        def i2b64(v):
            raw = int(v).to_bytes(32, 'big')
            return helpers.b64urlencode(raw, strip=True)

        def b2b64(b):
            return helpers.b64urlencode(b, strip=True)

        attest_payload = {
            'viewer_id': uuid.uuid4().hex,
            'device_id': uuid.uuid4().hex,
            'challenge_id': challenge['challenge_id'],
            'nonce': challenge['nonce'],
            'signature': b2b64(signature),
            'public_key': {
                'kty': 'EC', 'crv': 'P-256',
                'x': i2b64(key.pointQ.x),
                'y': i2b64(key.pointQ.y),
                'ext': True, 'key_ops': ['verify'],
            },
            'client': {
                'user_agent': common.FF_USER_AGENT,
                'platform': 'Windows',
                'languages': ['en-US', 'en'],
                'timezone': 'Europe/Rome',
                'hardware_concurrency': 8,
                'touch_points': 0,
            },
            'storage': {},
            'attributes': {'entropy': 'low'},
        }

        attest_url = '{0}/api/videos/access/attest'.format(origin)
        attest = json.loads(
            self.net.http_POST(attest_url, headers=headers, form_data=attest_payload, jdata=True).content
        )

        return {
            'fingerprint': {
                'token': attest['token'],
                'viewer_id': attest['viewer_id'],
                'device_id': attest['device_id'],
                'confidence': attest['confidence'],
            }
        }

    @staticmethod
    def fp_simple(x, y, z):
        """Simple SHA256-signed fingerprint fallback."""
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
            'exp': ctime + 600,
        }
        t_bdata = helpers.b64urlencode(json.dumps(t_data), strip=True)
        t_sig = helpers.b64urlencode(sha256(t_bdata.encode()).digest(), strip=True)
        token = '{0}.{1}'.format(t_bdata, t_sig)
        t_data.update({'token': token})
        t_data.pop('iat')
        t_data.pop('exp')
        return {'fingerprint': t_data}
