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
import hmac
import hashlib
import os
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.lib.aesgcm import python_aesgcm
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class ByseResolver(ResolveUrl):
    name = 'Byse'
    domains = [
        'f16px.com', 'bysesayeveum.com', 'bysetayico.com', 'bysevepoin.com', 'bysezejataos.com',
        'bysekoze.com', 'bysesukior.com', 'bysejikuar.com', 'bysefujedu.com', 'bysedikamoum.com',
        'bysebuho.com', "byse.sx", 'filemoon.sx', 'filemoon.to', 'filemoon.in', 'filemoon.link', 'filemoon.nl',
        'filemoon.wf', 'cinegrab.com', 'filemoon.eu', 'filemoon.art', 'moonmov.pro', '96ar.com',
        'kerapoxy.cc', 'furher.in', '1azayf9w.xyz', '81u6xl9d.xyz', 'smdfs40r.skin', 'c1z39.com',
        'bf0skv.org', 'z1ekv717.fun', 'l1afav.net', '222i8x.lol', '8mhlloqo.fun', 'f51rm.com',
        'xcoic.com', 'boosteradx.online', 'streamlyplayer.online', 'bysewihe.com'
    ]
    pattern = r'(?://|\.)((?:filemoon|cinegrab|moonmov|kerapoxy|furher|1azayf9w|81u6xl9d|f16px|' \
              r'smdfs40r|bf0skv|z1ekv717|l1afav|222i8x|8mhlloqo|96ar|xcoic|f51rm|c1z39|boosteradx|' \
              r'byse(?:sayeveum|tayico|vepoin|zejataos|koze|sukior|jikuar|fujedu|dikamoum|buho|wihe)?)' \
              r'\.(?:sx|to|s?k?in|link|nl|wf|com|eu|art|pro|cc|xyz|org|fun|net|lol|online))' \
              r'/(?:(?:e|d|download)/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': 'https://{0}/e/{1}'.format(host, media_id),
            'Origin': 'https://{0}'.format(host),
            'Content-Type': 'application/json',
        }

        body = json.dumps(self._make_fingerprint()).encode('utf-8')
        html = self.net.http_POST(web_url, form_data=body, headers=headers).content
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
            iv  = self.ft(pd.get('iv'))
            key = self.xn(pd.get('key_parts'))
            pl  = self.ft(pd.get('payload'))
            cipher = python_aesgcm.new(key)
            ct = cipher.open(iv, pl)
            if ct is None:
                # fallback: try payload2 with decrypt_keys
                ct = self._try_payload2(pd)
            if ct:
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

    def _try_payload2(self, pd):
        """Fallback: try payload2 against each decrypt_key."""
        decrypt_keys = pd.get('decrypt_keys') or {}
        iv2  = pd.get('iv2')
        pay2 = pd.get('payload2')
        if not (iv2 and pay2 and decrypt_keys):
            return None
        iv2  = self.ft(iv2)
        pay2 = self.ft(pay2)
        for key_b64 in decrypt_keys.values():
            try:
                key2   = self.ft(key_b64)
                cipher = python_aesgcm.new(key2)
                result = cipher.open(iv2, pay2)
                if result:
                    return result
            except Exception:
                continue
        return None

    @staticmethod
    def _b64url_encode(data):
        import base64
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

    @staticmethod
    def _make_fingerprint():
        """Generate the fingerprint body the API expects."""
        viewer_id = ByseResolver._b64url_encode(os.urandom(16))
        device_id = ByseResolver._b64url_encode(os.urandom(16))
        now = int(time.time())

        token_payload = {
            'viewer_id': viewer_id,
            'device_id': device_id,
            'confidence': 0.93,
            'iat': now,
            'exp': now + 600,
        }
        payload_b64 = ByseResolver._b64url_encode(
            json.dumps(token_payload, separators=(',', ':')).encode()
        )
        sig = hmac.new(b'', payload_b64.encode(), hashlib.sha256).digest()
        token = '{0}.{1}'.format(payload_b64, ByseResolver._b64url_encode(sig))

        return {
            'fingerprint': {
                'token': token,
                'viewer_id': viewer_id,
                'device_id': device_id,
                'confidence': 0.93,
            }
        }

    @staticmethod
    def ft(e):
        t = e.replace('-', '+').replace('_', '/')
        r = 0 if len(t) % 4 == 0 else 4 - len(t) % 4
        n = t + '=' * r
        return helpers.b64decode(n, binary=True)

    def xn(self, e):
        t = list(map(self.ft, e))
        return b''.join(t)
