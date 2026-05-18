"""
    Plugin for ResolveURL
    Copyright (C) 2026 icarok99

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
import json
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib import helpers


class VrraTopResolver(ResolveUrl):
    name = 'VrraTop'
    domains = ['vrra.top']
    pattern = r'(?://|\.)(vrra\.top)/(?:e|embed)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        import cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )

        web_url = self.get_url(host, media_id)
        
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': web_url,
            'Origin': f'https://{host}',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest'
        }

        try:
            r = scraper.get(web_url, headers=headers, timeout=20)
            html = r.text

            handshake = re.search(r'HANDSHAKE\s*=\s*["\']([^"\']{60,})["\']', html)
            if not handshake:
                handshake = re.search(r'var HANDSHAKE\s*=\s*["\']([^"\']{60,})["\']', html)
            if not handshake:
                handshake = re.search(r'"h"\s*:\s*["\']([^"\']{60,})["\']', html)

            if not handshake:
                raise ResolverError('No playable video found.')

            handshake = handshake.group(1)

            api_url = f'https://{host}/api/manifest'
            payload = {'h': handshake}

            resp = scraper.post(api_url, json=payload, headers=headers, timeout=15).text
            data = json.loads(resp)

            if data and data.get('url'):
                stream_url = data['url']
                return stream_url + helpers.append_headers({
                    'User-Agent': headers['User-Agent'],
                    'Referer': web_url,
                    'Origin': f'https://{host}'
                })

            raise ResolverError('No playable video found.')

        except Exception:
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
