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
    domains = ['vk.com', 'vkvideo.ru']
    pattern = r'(?://|\.)(vk(?:video)?\.(?:com|ru))/(?:video_ext\.php\?)?(.+)'

    def get_media_url(self, host, media_id):
        ref = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.EDGE_USER_AGENT,
                   'Referer': ref,
                   'Origin': ref[:-1]}

        video_list = ''
        try:
            query = urllib_parse.parse_qs(media_id)
            oid, video_id = query['oid'][0], query['id'][0]
        except:
            if '_' in media_id:
                oid, video_id = re.findall('(.*)_(.*)', media_id)[0]
                if 'list=' in media_id:
                    video_list = re.findall('list=(.*)', media_id)[0]
            else:
                pass

        if 'doc/' not in media_id and not media_id.startswith('doc'):
            oid = oid.replace('video', '')
            sources = self.__get_sources(host, oid, video_id, headers, video_list)
            if sources:
                sources.sort(key=lambda x: int(x[0]), reverse=True)
                source = helpers.pick_source(sources)
                if source:
                    headers.pop('X-Requested-With')
                    return source + helpers.append_headers(headers)

        html = self.net.http_GET(self.get_url(host, media_id), headers=headers).content
        if 'doc/' in media_id or media_id.startswith('doc'):
            jd = re.search(r'Docs\.initDoc\(({.+?})\)', html)
        else:
            jd = re.search(r'var\s*playerParams\s*=\s*(.+?});', html)
        if jd:
            jd = json.loads(jd.group(1))
            if 'doc/' in media_id or media_id.startswith('doc'):
                source = jd.get('docUrl')
            else:
                params = jd.get('params')[0]
                source = params.get('hls') or params.get('hls_ondemand')
            if source:
                return source + helpers.append_headers(headers)

        raise ResolverError('No video found')

    def __get_sources(self, host, oid, video_id, headers={}, video_list=''):
        sources_url = 'https://{0}/al_video.php?act=show'.format(host)
        data = {
            'act': 'show',
            'al': 1,
            'video': '{0}_{1}'.format(oid, video_id)
        }
        if video_list:
            data.update({
                'list': video_list,
                'load_playlist': 1,
                'module': 'direct',
                'show_next': 1,
                'playlist_id': '{0}_-2'.format(oid)
            })
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
                str_url = js_data.get('hls') or js_data.get('hls_live')
                if str_url:
                    sources = [('360', str_url)]
        return sources

    def get_url(self, host, media_id):
        if 'doc/' in media_id or media_id.startswith('doc'):
            url = 'https://{0}/{1}'.format(host, media_id)
        else:
            media_id = media_id.replace('video', '')
            url = 'https://{0}/video_ext.php?{1}'.format(host, media_id)
        return url
