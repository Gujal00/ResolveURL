"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class DeadlyBloggerResolver(ResolveUrl):
    name = 'DeadlyBlogger'
    domains = ['deadlyblogger.com']
    pattern = r'(?://|\.)(deadlyblogger\.com)/((?:.+/)?(?:.+\.html))'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        if web_url.endswith('.html'):
            # Some links are just direct mp4 renamed to html or redirecting
            # According to Kotlin: url.dropLast(5) + ".mp4"
            mp4_url = web_url[:-5] + ".mp4"
            
            # Check if direct mp4 works or if we need to scrape
            headers = {'User-Agent': common.RAND_UA}
            
            # Try scraping first as per Kotlin logic which preference-checks page content
            html = self.net.http_GET(web_url, headers=headers).content
            match = re.search(r'<source\s+src=["\']([^"\']+)["\']', html)
            if match:
                src = match.group(1)
                if not src.startswith('http'):
                    base = web_url.rsplit('/', 1)[0] + '/'
                    src = base + src
                return src + helpers.append_headers(headers)
            
            # Fallback to .mp4 rewrite if no source found in html
            return mp4_url + helpers.append_headers(headers)

        return web_url

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
