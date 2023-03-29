"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common


class SecVideoResolver(ResolveUrl):
    name = 'SecVideo'
    domains = ['secvideo1.online', 'csst.online']
    pattern = r'(?://|\.)((?:secvideo1|csst)\.online)/(?:videos|embed)/([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        srcs = re.search(r'Playerjs.+?file:"([^"]+)', html, re.DOTALL)
        if srcs:
            srcs = srcs.group(1).split(',')
            srcs = [(x.split(']')[0][1:], x.split(']')[1]) for x in srcs]
            return helpers.pick_source(helpers.sort_sources_list(srcs)) + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}/')
