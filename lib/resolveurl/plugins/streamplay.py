# -*- coding: UTF-8 -*-
"""
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


class StreamplayResolver(ResolveUrl):
    name = "streamplay"
    domains = ["streamplay.to", "streamplay.club", "streamplay.top", "streamplay.me"]
    pattern = '(?://|\.)(streamplay\.(?:to|club|top|me))/(?:embed-|player-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA, 'Referer': web_url.replace('/player-', '/preview-')}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            var = re.search('var _0x[0-f]+=\[([^;]+)\];', html)
            sources = helpers.scrape_sources(html, patterns=['''(?P<url>http[^,]+\.(?:mp4|m3u8))'''])
            if sources and var:
                headers.update({'Referer': web_url})
                sources = [(source[0], self.decode_video_url(source[1])) for source in sources]

                return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://streamplay.me/player-{media_id}.html')
        
    def decode_video_url(self, url):
        tria = re.compile('[0-9a-z]{40,}', re.IGNORECASE).findall(url)[0]
        gira = tria[::-1]
        x = gira[:2] + gira[3:]
        
        return re.sub(tria, x, url)
