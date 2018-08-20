"""
VK resolveurl XBMC Addon
Copyright (C) 2015 tknorris

Version 0.0.1 

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
import json
import urllib
import urlparse
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VKResolver(ResolveUrl):
    name = "VK.com"
    domains = ["vk.com"]
    pattern = '(?://|\.)(vk\.com)/(?:video_ext\.php\?|video)(.+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        headers = {
            'User-Agent': common.EDGE_USER_AGENT
        }

        query = urlparse.parse_qs(media_id)

        try: oid, video_id = query['oid'][0], query['id'][0]
        except: oid, video_id = re.findall('(.*)_(.*)', media_id)[0]

        sources = self.__get_sources(oid, video_id)
        sources.sort(key=lambda x: int(x[0]), reverse=True)

        source = helpers.pick_source(sources)
        return source + helpers.append_headers(headers)
        raise ResolverError('No video found')

    def __get_sources(self, oid, video_id):
        sources_url = 'http://vk.com/al_video.php?act=show_inline&al=1&video=%s_%s' % (oid, video_id)
        html = self.net.http_GET(sources_url).content
        html = re.sub(r'[^\x00-\x7F]+', ' ', html)

        sources = re.findall('(\d+)x\d+.+?(http.+?\.m3u8.+?)n', html)

        if not sources:
            sources = re.findall('"url(\d+)"\s*:\s*"(.+?)"', html)

        sources = [(i[0], i[1].replace('\\', '')) for i in sources]

        return sources

    def get_url(self, host, media_id):
        return 'http://vk.com/video_ext.php?%s' % (media_id)
