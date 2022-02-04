"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class RoVideoResolver(ResolveUrl):
    name = "rovideo"
    domains = ['rovideo.net']
    pattern = r'(?://|\.)(rovideo\.net)/(?:embed|videos)/([0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        alt_url = re.search(r'<link\s*href="([^"]+)', html)
        if alt_url:
            headers.update({'Referer': web_url})
            html = self.net.http_GET(alt_url.group(1), headers=headers).content
            url = re.findall(r"video_url:\s*'([^']+)", html)
            if url:
                url = url[0]
                if url.startswith('function/'):
                    lcode = re.findall(r"license_code:\s*'([^']+)", html)[0]
                    url = helpers.fun_decode(url, lcode)
                return url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/embed/{media_id}/')
