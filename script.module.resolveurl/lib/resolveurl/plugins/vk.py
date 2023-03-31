"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
import json
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VKResolver(ResolveUrl):
    name = 'VK'
    domains = ['vk.com']
    pattern = r'(?://|\.)(vk\.com)/(?:video_ext\.php\?|video)(.+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.EDGE_USER_AGENT,
                   'Referer': 'https://vk.com/',
                   'Origin': 'https://vk.com'}

        query = urllib_parse.parse_qs(media_id)

        try:
            oid, video_id = query['oid'][0], query['id'][0]
        except:
            oid, video_id = re.findall('(.*)_(.*)', media_id)[0]

        sources = self.__get_sources(oid, video_id, headers)
        if sources:
            sources.sort(key=lambda x: int(x[0]), reverse=True)
            source = helpers.pick_source(sources)
            if source:
                return source + helpers.append_headers(headers)

        raise ResolverError('No video found')

    def __get_sources(self, oid, video_id, headers={}):
        sources_url = 'https://vk.com/al_video.php?act=show'
        data = {
            'act': 'show',
            'al': 1,
            'video': '{0}_{1}'.format(oid, video_id)
        }
        headers.update({'X-Requested-With': 'XMLHttpRequest'})
        html = self.net.http_POST(sources_url, form_data=data, headers=headers).content

        if html.startswith('<!--'):
            html = html[4:]
        js_data = json.loads(html)
        payload = []
        sources = []
        for item in js_data.get('payload'):
            if isinstance(item, list):
                payload = item
        if payload:
            for item in payload:
                if isinstance(item, dict):
                    js_data = item.get('player').get('params')[0]
            for item in list(js_data.keys()):
                if item.startswith('url'):
                    sources.append((item[3:], js_data.get(item)))
            if not sources:
                sources = [('360', js_data.get('hls'))]
            return sources
        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return 'https://vk.com/video_ext.php?%s' % (media_id)
