"""
    Plugin for ResolveURL
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

import json
import re
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import random


class IndaVideoResolver(ResolveUrl):
    name = 'IndaVideo'
    domains = ['indavideo.hu']
    pattern = r'(?://|\.)(indavideo\.hu)/(?:player/video|video)/([0-9A-Za-z-_]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        data = json.loads(html)

        if data['success'] == '0':
            html = self.net.http_GET('http://indavideo.hu/video/%s' % media_id).content
            emb_hash = re.search(r'emb_hash.+?value\s*=\s*"([^"]+)', html)
            if not emb_hash:
                raise ResolverError('File not found')

            web_url = self.get_url(host, emb_hash.group(1))

            html = self.net.http_GET(web_url).content
            data = json.loads(html)

        if data['success'] == '1':
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
            sources = sorted(sources, key=lambda x: x[0])[::-1]
            return helpers.pick_source(sources)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        rnd_number = random.randrange(2147483647)
        return 'http://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/%s/?_=%d' % (media_id, rnd_number)
