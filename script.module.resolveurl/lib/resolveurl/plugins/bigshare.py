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

import re
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class BigShareResolver(ResolveUrl):
    name = 'BigShare'
    domains = ['bigshare.io']
    pattern = r'(?://|\.)(bigshare\.io)/watch/(?:e/)?([a-zA-Z0-9]+)'

    def get_media_url(self, host, media_id):
        import cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
            delay=4
        )
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': urllib_parse.urljoin(web_url, '/'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        r = scraper.get(web_url, headers=headers, timeout=15, allow_redirects=True)

        if r.url != web_url:
            web_url = r.url
            headers['Referer'] = urllib_parse.urljoin(web_url, '/')

        html = r.text

        match = re.search(r'''url:\s*'(?P<url>https://cdn\.bigshare\.io/[^']+)''', html)
        if match:
            return match.group('url') + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/watch/e/{media_id}')
