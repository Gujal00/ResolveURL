# -*- coding: UTF-8 -*-
"""
    Kodi resolveurl plugin
    Copyright (C) 2017  zlootec

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

class VidstoreResolver(ResolveUrl):
    name = "vidstore"
    domains = ["vidstore.me"]
    pattern = '(?://|\.)(vidstore\.me)/(.+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        sources = re.findall('''<source\s+src\s*=\s*['"]([^'"]+).+?label\s*=\s*['"]([^'"]+)''', html, re.DOTALL)
        if not sources: 
            raise ResolverError('File not found')
        sources = [(i[1], i[0]) for i in sources]
        sources = sorted(sources, key=lambda x: x[0])[::-1]
        
        source = 'http://www.%s%s' % (host, helpers.pick_source(sources))
        headers['Referer'] = web_url
        source = self.net.http_GET(source, headers=headers).get_url()
        return source

    def get_url(self, host, media_id):
        return 'http://www.%s/%s' % (host, media_id)
