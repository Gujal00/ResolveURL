# -*- coding: UTF-8 -*-
"""
    Kodi resolveurl plugin
    Copyright (C) 2016  alifrezser

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
from resolveurl.resolver import ResolveUrl, ResolverError

class Toltsd_felResolver(ResolveUrl):
    name = "toltsd-fel"
    domains = ["toltsd-fel.tk", "toltsd-fel.xyz"]
    pattern = '(?://|\.)(toltsd-fel\.(?:tk|xyz))/(?:embed|video)/([0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        direct_url = re.search('m4v\s*:\s*["\']([^"\']+)', html)
        if direct_url:
            return direct_url.group(1)
        
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/embed/{media_id}')
