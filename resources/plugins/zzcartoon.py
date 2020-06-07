"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class ZZCarttonResolver(ResolveUrl):
    name = 'zzcartoon'
    domains = ['zzcartoon.com']
    pattern = r'(?://|\.)((?:zzcartoon)\.com)/(?:embed)/(\d+)'
    pattern2 = r'(?://|\.)((?:zzcartoon)\.com)/(?:videos)/([-\w]+)\.html'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.RAND_UA}
        if not media_id.isdigit():
            web_url = self.get_url(host, media_id)
            html = self.net.http_GET(web_url, headers=headers).content
            r = re.search(r"""<iframe\s*width=['"]\d+['"]\s*height=['"]\d+['"]\s*src=['"](http:\/\/www\.zzcartoon\.com\/embed\/(\d+))""", html)
            if r:
                web_url = r.group(1)
            else:
                raise ResolverError('File not found')
        else:
            web_url = self.get_url(host, media_id)

        html2 = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'''video_url:\s*['"]([^"']+)''', html2, re.DOTALL)
        if r:
            return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_host_and_id(self, url):
        if '/embed' not in url:
            r = re.search(self.pattern2, url, re.I)
        else:
            r = re.search(self.pattern, url, re.I)
        if r:
            return r.groups()
        else:
            return False

    def get_url(self, host, media_id):
        if not media_id.isdigit():
            return self._default_get_url(host, media_id, template='http://www.{host}/videos/{media_id}.html')
        else:
            return self._default_get_url(host, media_id, template='http://www.{host}/embed/{media_id}')

    def valid_url(self, url, host):
        return re.search(self.pattern, url, re.I) or re.search(self.pattern2, url, re.I) or self.name in host

    @classmethod
    def _is_enabled(cls):
        return True
