# -*- coding: UTF-8 -*-
"""
    Kodi resolveurl plugin
    Copyright (C) 2016 alifrezser

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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class WatchonlineResolver(ResolveUrl):
    name = "watchonline"
    domains = ["watchonline.to"]
    pattern = '(?://|\.)(watchonline\.to)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}

        html = self.net.http_GET(web_url, headers=headers).content

        match = re.search('file\s*:\s*["\']([^"\']+)', html)
        if not match:
            raise ResolverError('File Not Found or removed')
        else:
            source = match.group(1)

        html = self.net.http_GET(source).content
        html = html.replace('\n', '')

        sources = re.findall('RESOLUTION\s*=\s*([^,]+).+?(http[^\#]+)', html)
        sources.sort(key=lambda x: int(x[0].split('x')[0]), reverse=True)
        if not sources:
            raise ResolverError('File Not Found or removed')
        else:
            return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://www.%s/embed-%s.html' % (host, media_id)
