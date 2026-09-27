"""
    Plugin for ResolveURL
    Copyright (C) 2026 Twilight0

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class DTubeResolver(ResolveUrl):
    name = 'DTube'
    domains = ['d.tube', 'play.d.tube']
    pattern = r'(?://|\.)(d\.tube|play\.d\.tube)(?:/watch/|/embed/|/\?v=|\?v=)([0-9a-zA-Z_-]+)'

    def get_media_url(self, host, media_id, subs=False):
        api_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA, 'Referer': 'https://d.tube/'}
        try:
            res = self.net.http_GET(api_url, headers=headers)
            data = res.json
        except Exception:
            raise ResolverError('File Not Found or removed')

        stream_url = data.get('video_url')
        if not stream_url:
            raise ResolverError('Unable to locate stream URL')

        stream_url += helpers.append_headers(headers)

        if subs:
            subtitles = {}
            video_uuid = data.get('id')
            if video_uuid:
                sub_url = 'https://nas1.d.tube/transcripts/{0}.vtt'.format(video_uuid)
                try:
                    sub_res = self.net.http_GET(sub_url, headers=headers)
                    if sub_res:
                        match = re.search(r'NOTE Language:\s*(\S+)', sub_res.content)
                        lang = match.group(1) if match else 'und'
                        subtitles[lang] = sub_url
                except Exception:
                    pass
            return stream_url, subtitles

        return stream_url

    def get_url(self, host, media_id):
        return 'https://api.d.tube/videos/{0}'.format(media_id)
