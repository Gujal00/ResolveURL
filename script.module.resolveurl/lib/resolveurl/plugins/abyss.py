"""
    Plugin for ResolveURL
    Copyright (C) 2025

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
import hashlib
import re
import base64
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.lib.pyaes.aes import AESModeOfOperationCTR, Counter
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

import cloudscraper

class AbyssResolver(ResolveUrl):
    name = 'Abyss'
    domains = [
        'abysscdn.com',
        'hydraxcdn.biz',
        'short.icu',
    ]
    pattern = (
        r'(?://|\.)((?:abysscdn|hydraxcdn)\.(?:com|biz)|short\.icu)'
        r'(?:/\?v=|/)([0-9a-zA-Z_-]+)'
    )

    _CHARSET = 'RB0fpH8ZEyVLkv7c2i6MAJ5u3IKFDxlS1NTsnGaqmXYdUrtzjwObCgQP94hoeW+/='

    def __init__(self):
        super(AbyssResolver, self).__init__()
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
            delay=4
        )

    def get_media_url(self, host, media_id):
        if host == 'short.icu':
            web_url = 'https://abysscdn.com/?v={0}'.format(media_id)
        else:
            web_url = self.get_url(host, media_id)

        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': urllib_parse.urljoin(web_url, '/'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        r = self.scraper.get(web_url, headers=headers, timeout=15)

        if r.url != web_url:
            web_url = r.url
            headers['Referer'] = urllib_parse.urljoin(web_url, '/')
        html = r.text

        datas = self._extract_datas_payload(html)
        if datas:
            slug       = datas.get('slug')
            md5_id     = datas.get('md5_id')
            user_id    = datas.get('user_id')
            media_blob = datas.get('media')

            if isinstance(media_blob, dict):
                media_payload = media_blob
            else:
                media_payload = self._decrypt_media(media_blob, user_id, slug, md5_id)

            source = self._extract_from_media_payload(media_payload, slug, md5_id)
            if source:
                return source + helpers.append_headers(headers)

        source = self._legacy_extract(html)
        if source:
            return source + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/?v={media_id}')

    def _extract_datas_payload(self, html):
        match = re.search(r'(?:const|var)\s+datas\s*=\s*"([^"]+)"', html or '')
        if not match:
            return {}

        try:
            raw = base64.b64decode(match.group(1).strip())
        except Exception:
            return {}

        try:
            payload = json.loads(raw.decode('utf-8'))
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass

        decoded = raw.decode('latin-1', 'ignore')
        payload = {}

        for key, pat in [
            ('slug',    r'"slug"\s*:\s*"([^"]+)"'),
            ('md5_id',  r'"md5_id"\s*:\s*(\d+)'),
            ('user_id', r'"user_id"\s*:\s*(\d+)'),
        ]:
            m = re.search(pat, decoded)
            if m:
                payload[key] = int(m.group(1)) if key != 'slug' else m.group(1)

        media_marker  = b'"media":"'
        config_marker = b'","config"'
        m_idx = raw.find(media_marker)
        c_idx = raw.find(config_marker)
        if m_idx >= 0 and c_idx > m_idx:
            try:
                media_escaped    = raw[m_idx + len(media_marker):c_idx].decode('latin-1', 'ignore')
                payload['media'] = self._decode_escaped_binary(media_escaped)
            except Exception:
                pass
        elif 'media' not in payload:
            m = re.search(r'"media"\s*:\s*"((?:\\.|[^"\\])*)"', decoded, re.DOTALL)
            if m:
                payload['media'] = self._decode_escaped_binary(m.group(1))

        return payload if payload else {}

    def _decode_escaped_binary(self, escaped):
        if not escaped:
            return ''
        out = []
        i = 0
        esc_map = {'n': '\n', 'r': '\r', 't': '\t', 'b': '\b',
                   'f': '\f', '\\': '\\', '"': '"', '/': '/'}
        while i < len(escaped):
            ch = escaped[i]
            if ch == '\\' and i + 1 < len(escaped):
                nxt = escaped[i + 1]
                if nxt == 'u' and i + 5 < len(escaped):
                    try:
                        out.append(chr(int(escaped[i + 2:i + 6], 16)))
                        i += 6
                        continue
                    except Exception:
                        pass
                if nxt in esc_map:
                    out.append(esc_map[nxt])
                    i += 2
                    continue
            out.append(ch)
            i += 1
        return ''.join(out)

    def _derive_key(self, seed):
        seed_str = str(seed)
        if seed_str.replace('.', '', 1).replace(':', '').replace('-', '').isdigit():
            buf = bytearray()
            for ch in seed_str:
                buf.append(int(ch) if ch.isdigit() else (ord(ch) & 0xFF))
            digest_source = bytes(buf)
        else:
            digest_source = seed_str.encode('utf-8')
        return bytearray(hashlib.md5(digest_source).hexdigest().encode('utf-8'))

    def _aes_ctr_transform(self, data_bytes, key_seed):
        key = self._derive_key(key_seed)
        iv  = key[:16]
        try:
            counter = Counter(initial_value=int.from_bytes(bytes(iv), 'big'))
            cipher  = AESModeOfOperationCTR(bytes(key), counter=counter)
            return bytes(cipher.encrypt(bytes(data_bytes)))
        except Exception as e:
            return None

    def _decrypt_media(self, encrypted_text, user_id, slug, md5_id):
        if not encrypted_text or not user_id or not slug or not md5_id:
            return {}
        key_seed  = '{0}:{1}:{2}'.format(user_id, slug, md5_id)
        raw_bytes = bytes(ord(ch) & 0xFF for ch in encrypted_text)
        result    = self._aes_ctr_transform(raw_bytes, key_seed)
        if not result:
            return {}
        try:
            decoded = json.loads(result.decode('utf-8', 'ignore'))
            return decoded if isinstance(decoded, dict) else {}
        except Exception as e:
            return {}

    def _build_sora_token(self, path_value, size_value):
        transformed = self._aes_ctr_transform(path_value.encode('utf-8'), str(size_value))
        if not transformed:
            return None
        first  = base64.b64encode(transformed).decode('utf-8').replace('=', '')
        second = base64.b64encode(first.encode('utf-8')).decode('utf-8').replace('=', '')
        return second

    def _extract_from_media_payload(self, media_payload, slug, md5_id):
        if not isinstance(media_payload, dict):
            return None

        mp4     = media_payload.get('mp4') if isinstance(media_payload.get('mp4'), dict) else {}
        raw_sources = mp4.get('sources') if isinstance(mp4.get('sources'), list) else []
        sources = sorted(
            [s for s in raw_sources if isinstance(s, dict)],
            key=lambda s: int(s.get('size', 0) or 0),
            reverse=True
        )
        for src in sources:
            direct = src.get('file')
            if isinstance(direct, str) and direct:
                return direct.replace('\\/', '/')
            url_  = src.get('url')
            path_ = src.get('path')
            if isinstance(url_, str) and isinstance(path_, str) and url_ and path_:
                return '{0}/{1}'.format(url_.rstrip('/'), path_.lstrip('/')).replace('\\/', '/')

        hls = media_payload.get('hls') if isinstance(media_payload.get('hls'), dict) else {}
        for key in ('file', 'url', 'master', 'src', 'source'):
            val = hls.get(key)
            if isinstance(val, str) and val:
                return val.replace('\\/', '/')
        for hs in (hls.get('sources') or []):
            if not isinstance(hs, dict):
                continue
            f = hs.get('file') or hs.get('url') or hs.get('src')
            if isinstance(f, str) and f:
                return f.replace('\\/', '/')

        domains = mp4.get('domains') if isinstance(mp4.get('domains'), list) else []
        for src in sources:
            size   = src.get('size')
            res_id = src.get('res_id')
            sub    = src.get('sub')
            if not (size and res_id and sub and md5_id and slug):
                continue
            domain = next((d for d in domains if isinstance(d, str) and sub in d), None)
            if not domain:
                continue
            path_value = '/mp4/{0}/{1}/{2}?v={3}'.format(md5_id, res_id, size, slug)
            token = self._build_sora_token(path_value, str(size))
            if token:
                norm = domain if domain.startswith('http') else 'https://' + domain
                url  = '{0}/sora/{1}/{2}'.format(norm.rstrip('/'), size, token)
                return url

        hls_id = hls.get('id')
        if hls_id:
            url = 'https://abysscdn.com/#hls/{0}/master.m3u8'.format(hls_id)
            return url

        return None

    def _custom_decode(self, encoded):
        out = bytearray()
        for i in range(0, len(encoded), 4):
            chunk = encoded[i:i + 4].ljust(4, '=')
            c = [self._CHARSET.index(ch) if ch in self._CHARSET else 64 for ch in chunk]
            out.append((c[0] << 2) | (c[1] >> 4))
            if c[2] != 64:
                out.append(((c[1] & 15) << 4) | (c[2] >> 2))
            if c[3] != 64:
                out.append(((c[2] & 3) << 6) | c[3])
        return out.decode('utf-8', 'ignore')

    def _legacy_extract(self, html):
        m = re.search(
            r"[\w$]+=\'([A-Za-z0-9+/=RB0fpH8ZEyVLkv7c2i6MAJ5u3IKFDxlS1NTsnGaqmXYdUrtzjwObCgQP94hoeW]{30,})_\'",
            html or ''
        )
        if m:
            try:
                meta   = json.loads(self._custom_decode(m.group(1)))
                domain = meta.get('domain', '')
                vid_id = meta.get('id', '')
                if domain and vid_id:
                    url = 'https://{0}/{1}'.format(domain.strip('/'), vid_id)
                    return url
            except Exception:
                pass

        dm = re.search(r"['\"]domain['\"]\s*:\s*['\"]([^'\"]+)['\"]", html or '')
        im = re.search(r"['\"]id['\"]\s*:\s*['\"](['\"]edns[^'\"]+)['\"]", html or '')
        if dm and im:
            url = 'https://{0}/{1}'.format(dm.group(1).strip('/'), im.group(1))
            return url

        return None
