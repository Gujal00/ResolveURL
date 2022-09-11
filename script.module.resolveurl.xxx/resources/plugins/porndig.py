"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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


class PornDigResolver(ResolveUrl):
    name = 'porndig'
    domains = ['porndig.com']
    pattern = r'(?://|\.)(porndig\.com)/videos/(\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'''<iframe.+?src=["'](https://videos\.porndig\.com/player/index/[\d/]+)''', html)
        if r:
            return helpers.get_media_url(
                r.group(1),
                patterns=[r'src":\s*"(?P<url>[^"]+)",\s*"type":\s*"[^"]+",\s*"label":\s*"(?P<label>[^"]+)'],
                generic_patterns=False
            ).replace(' ', '%20')

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/videos/{media_id}/')

    @classmethod
    def _is_enabled(cls):
        return True
