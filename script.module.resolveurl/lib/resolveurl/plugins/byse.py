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
import os
import base64
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.lib.aesgcm import python_aesgcm
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class ByseResolver(ResolveUrl):
    name = 'Byse'
    domains = [
        'f16px.com', 'bysesayeveum.com', 'bysetayico.com',
        'bysevepoin.com', 'bysezejataos.com', 'bysekoze.com',
        'bysesukior.com', 'bysejikuar.com', 'bysefujedu.com',
        'bysedikamoum.com', 'bysebuho.com', 'byse.sx',
        'filemoon.sx', 'filemoon.to', 'filemoon.in', 'filemoon.link',
        'filemoon.wf', 'cinegrab.com', 'filemoon.eu', 'filemoon.art',
        'moonmov.pro', '96ar.com', 'kerapoxy.cc', 'furher.in',
        '1azayf9w.xyz', '81u6xl9d.xyz', 'smdfs40r.skin', 'c1z39.com',
        'bf0skv.org', 'z1ekv717.fun', 'l1afav.net', '222i8x.lol',
        '8mhlloqo.fun', 'f51rm.com', 'xcoic.com', 'filemoon.nl',
        'boosteradx.online', 'streamlyplayer.online',
        'bysewihe.com', 'byselapuix.com', 'embedplaybyse.top'
    ]
    pattern = (
        r'(?://|\.)((?:filemoon|cinegrab|moonmov|kerapoxy|furher'
        r'|1azayf9w|81u6xl9d|f16px|smdfs40r|bf0skv|z1ekv717|l1afav'
        r'|222i8x|8mhlloqo|96ar|xcoic|f51rm|c1z39|boosteradx'
        r'|embedplaybyse|byse(?:sayeveum|tayico|vepoin|zejataos|koze|sukior'
        r'|jikuar|fujedu|dikamoum|buho|wihe|lapuix)?)'
        r'\.(?:sx|to|s?k?in|link|nl|wf|com|eu|art|pro|cc'
        r'|xyz|org|fun|net|lol|online|top))'
        r'/(?:(?:e|d|download)/)?([0-9a-zA-Z]+)'
    )

    def get_media_url(self, host, media_id):
        base_url = f"https://{host}"
        ref = f"{base_url}/"

        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': ref,
            'Origin': base_url,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        }

        try:
            challenge_url = f"{base_url}/api/videos/access/challenge"
            challenge_resp = self.net.http_POST(
                challenge_url, form_data={}, headers=headers, jdata=True
            )
            challenge_data = json.loads(challenge_resp.content)
            if not challenge_data.get('challenge_id'):
                return self._get_media_url_legacy(host, media_id)

            attest_url = f"{base_url}/api/videos/access/attest"
            attest_payload = self.generate_attest_payload(challenge_data)
            try:
                self.net.http_POST(
                    attest_url,
                    form_data=attest_payload,
                    headers=headers,
                    jdata=True
                )
            except Exception:
                pass

            playback_url = f"{base_url}/api/videos/{media_id}/embed/playback"
            fingerprint = self.fp(16, 0.6, 0.9)

            response = self.net.http_POST(
                playback_url, form_data=fingerprint, headers=headers, jdata=True
            )
            data = json.loads(response.content)
        except Exception:
            return self._get_media_url_legacy(host, media_id)

        sources = data.get('sources')
        if sources:
            sources = [(x.get('label'), x.get('url')) for x in sources]
            uri = helpers.pick_source(helpers.sort_sources_list(sources))
            if uri.startswith('/'):
                uri = urllib_parse.urljoin(base_url, uri)
            url = helpers.get_redirect_url(uri, headers=headers)
            return url + helpers.append_headers(headers)

        pd = data.get('playback')
        if pd:
            iv = self.ft(pd.get('iv'))
            key = self.xn(pd.get('key_parts'))
            pl = self.ft(pd.get('payload'))

            cipher = python_aesgcm.new(key)
            ct = cipher.open(iv, pl)
            ct = json.loads(ct.decode('latin-1'))

            sources = ct.get('sources')
            if sources:
                sources = [
                    (x.get('label'), x.get('url')) for x in sources
                ]
                uri = helpers.pick_source(
                    helpers.sort_sources_list(sources)
                )
                return uri + helpers.append_headers(headers)

        return self._get_media_url_legacy(host, media_id)

    def _get_media_url_legacy(self, host, media_id):
        redirect_domains = ['boosteradx.online', 'byse.sx']
        if host in redirect_domains:
            host = 'streamlyplayer.online'
        web_url = self._default_get_url(host, media_id, 'https://{host}/api/videos/{media_id}/playback')
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': ref,
            'Origin': ref[:-1]
        }
        html = json.loads(self.net.http_POST(web_url, headers=headers, form_data=self.fp(16, 0.6, 0.9), jdata=True).content)
        sources = html.get('sources')
        if sources:
            sources = [(x.get('label'), x.get('url')) for x in sources]
            uri = helpers.pick_source(helpers.sort_sources_list(sources))
            if uri.startswith('/'):
                uri = urllib_parse.urljoin(web_url, uri)
            url = helpers.get_redirect_url(uri, headers=headers)
            return url + helpers.append_headers(headers)
        pd = html.get('playback')
        if pd:
            iv = self.ft(pd.get('iv'))
            key = self.xn(pd.get('key_parts'))
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

    def generate_attest_payload(self, challenge_data):
        viewer_id = self._random_hex(32)
        device_id = self._random_hex(32)

        return {
            "viewer_id": viewer_id,
            "device_id": device_id,
            "challenge_id": challenge_data["challenge_id"],
            "nonce": challenge_data["nonce"],
            "signature": (
                "Ncbrq_Q1SZEJg7HQnl_JIw07VPzhnjMUtSoDAObjxKjGVZZpNNN8"
                "6aTBH4fKwPhGsmRKx0t8P6RgZDv5vxU9LA"
            ),
            "public_key": {
                "crv": "P-256",
                "ext": True,
                "key_ops": ["verify"],
                "kty": "EC",
                "x": "YYzXQPV_N609nBkgwzY-nXuC7ybz1KQjCGhPWgVKUHc",
                "y": "y7tFcMQHg67Tjbmo3FyttBlfnO0mdY3nBuucIfBIyrQ"
            },
            "client": {
                "user_agent": common.FF_USER_AGENT,
                "platform": "Android",
                "platform_version": "13.0.0",
                "model": "SM-G780G",
                "pixel_ratio": 3,
                "screen_width": 360,
                "screen_height": 800,
                "color_depth": 24,
                "languages": ["pt-BR"],
                "timezone": "America/Recife",
                "hardware_concurrency": 8,
                "device_memory": 8,
                "touch_points": 5,
                "webgl_vendor": "Google Inc. (Qualcomm)",
                "webgl_renderer": (
                    "ANGLE (Qualcomm, Adreno (TM) 650, OpenGL ES 3.2)"
                ),
                "canvas_hash": "F-1yXhwdZJpJlwYoDcJslo6_GR6-u4TkTGOx25lcxDo",
                "audio_hash": "_VRYiH6_cygtD14eUnkys7AF3r7zCf769syVkS3GVGU",
                "pointer_type": "coarse,hover,touch"
            },
            "storage": {
                "cookie": viewer_id,
                "local_storage": viewer_id,
                "indexed_db": f"{viewer_id}:{device_id}",
                "cache_storage": f"{viewer_id}:{device_id}"
            },
            "attributes": {"entropy": "high"}
        }

    @staticmethod
    def _random_hex(length):
        return os.urandom(length // 2).hex()

    @staticmethod
    def _random_base64(length):
        return base64.urlsafe_b64encode(
            os.urandom(length)
        ).decode().rstrip('=')

    @staticmethod
    def ft(e):
        if not e:
            return b''
        t = e.replace('-', '+').replace('_', '/')
        return helpers.b64decode(t, binary=True)

    def xn(self, e):
        if not e:
            return b''
        import hashlib
        parts16 = [self.ft(p) for p in e if len(self.ft(p)) == 16]
        if len(parts16) >= 2:
            return parts16[0] + parts16[1]
        if len(parts16) == 1:
            return parts16[0]
        return hashlib.sha256(b''.join(self.ft(p) for p in e)).digest()

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
        t_sig = helpers.b64urlencode(
            sha256(t_bdata.encode()).digest(), strip=True
        )
        token = f"{t_bdata}.{t_sig}"

        t_data.update({'token': token})
        t_data.pop('iat')
        t_data.pop('exp')
        return {'fingerprint': t_data}
