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


class Porn00Resolver(ResolveUrl):
    name = 'porn00'
    domains = ['porn00.org', 'porn00.com']
    pattern = r'(?://|\.)(porn00\.org)/(?:video|plays|player)/\?v=(\d+)'
    pattern2 = r'(?://|\.)(porn00\.(?:org|com))/([\w\-]+)'

    def get_media_url(self, host, media_id):
        if not media_id.isdigit():
            web_url = self.get_url(host, media_id)
            headers = {'User-Agent': common.RAND_UA}
            html = self.net.http_GET(web_url, headers=headers).content
            video_ids = re.findall(r"""<iframe.+?src=["'].*?\?v=(\d+)["'&]""", html, re.I)
            if video_ids:
                video_id = video_ids[-1]
                return helpers.get_media_url('http://www.porn00.org/video/?v=%s' % video_id).replace(' ', '%20')

            raise ResolverError('File not found')
        else:
            return helpers.get_media_url(self.get_url(host, media_id)).replace(' ', '%20')

    def get_host_and_id(self, url):
        if '/?v=' not in url:
            r = re.search(self.pattern2, url, re.I)
        else:
            r = re.search(self.pattern, url, re.I)
        if r:
            return r.groups()
        else:
            return False

    def get_url(self, host, media_id):
        if not media_id.isdigit():
            return self._default_get_url(host, media_id, template='http://www.porn00.org/{media_id}/')
        else:
            return self._default_get_url(host, media_id, template='http://www.porn00.org/video/?v={media_id}')

    def valid_url(self, url, host):
        return re.search(self.pattern, url, re.I) or re.search(self.pattern2, url, re.I) or self.name in host

    @classmethod
    def _is_enabled(cls):
        return True
