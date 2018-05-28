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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VideaResolver(ResolveUrl):
    name = "videa"
    domains = ["videa.hu", "videakid.hu"]
    pattern = '(?://|\.)((?:videa|videakid)\.hu)/(?:player/?\?v=|videok/)(?:.*-|)([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        sources = helpers.get_dom(html, 'video_sources')
        if sources:
            sources = re.findall('name\s*=\s*[\'|"]([^\'"]+).+?streamable.+?>([^<]+)', sources[0])
            if sources[-1][0].lower() == 'lq': sources = sources[::-1]
            source = helpers.pick_source(sources)
            if source.startswith('//'): source = 'http:' + source
            return source

        raise ResolverError('Stream not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/videaplayer_get_xml.php?v={media_id}&start=0&referrer=http://{host}')
