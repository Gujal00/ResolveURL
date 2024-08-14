"""
    Plugin for ResolveURL
    Copyright (C) 2017 zlootec
    Copyright (C) 2024 MrDini123 (github.com/movieshark)

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
from json import loads
from time import time
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidStoreResolver(ResolveUrl):
    name = 'VidStore'
    domains = ['vidstore.me']
    pattern = r'(?://|\.)(vidstore\.me)/(.+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)

        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        sources = helpers.scrape_sources(
            html,
            patterns=[r'''<source\s*src=['"](?P<url>[^'"]+)['"]\s*type=['"]video/mp4['"]\s*label=['"](?P<label>[^'"]+)'''],
            generic_patterns=False
        )

        if subs:
            subtitles = helpers.scrape_subtitles(html, web_url)

        if sources:
            stream_url = helpers.pick_source(sources) + helpers.append_headers(headers)
            if subs:
                return stream_url, subtitles
            return stream_url

        if "indavideo.hu" in html:
            passwords = re.search(r'var passwords={(.+?)}', html)
            passwords = dict(re.findall(r'(?:",)?([^:]+):"([^"]+)', passwords.group(1)))
            url = re.search(r'settings={.+?url:"([^"]+)', html).group(1)
            html = self.net.http_GET(url + "?_=" + str(int(time() * 1000)), headers=headers).content
            data = loads(html)
            if data['success'] == '1':
                if not data.get('data', {}).get('video_files'):
                    username = data['data']['user_name']
                    password = passwords.get(username)
                    if not password:
                        raise ResolverError('Password not found')
                    url = "%s%s/%s" % (url, password, "?_=" + str(int(time() * 1000)))
                    html = self.net.http_GET(url, headers=headers).content
                    data = loads(html)
                # taken from indavideo resolver
                video_files = data['data']['video_files']
                if not video_files:
                    raise ResolverError('File removed')

                tokens = data['data']['filesh']

                sources = []
                if isinstance(video_files, dict):
                    video_files = list(video_files.values())
                for i in video_files:
                    match = re.search(r'\.(\d+)\.mp4', i)
                    if match:
                        sources.append((match.group(1), i))
                sources = [(i[0], i[1] + '&token=%s' % tokens[i[0]]) for i in sources]
                try:
                    sources = list(set(sources))
                except:
                    pass
                sources = sorted(sources, key=lambda x: int(x[0]), reverse=True)
                if subs:
                    return helpers.pick_source(sources) + helpers.append_headers(headers), subs
                return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/{media_id}')
