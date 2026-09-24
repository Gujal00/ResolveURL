"""
    Plugin for ResolveURL
    Copyright (C) 2026 TempleLain

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class TikTikStreamResolver(ResolveUrl):
    name = 'TikTikStream'
    domains = ['tiktikstream.com']
    pattern = r'(?://|\.)(tiktikstream\.com)/(?:v|embed)/([0-9A-Za-z_-]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        origin = urllib_parse.urljoin(web_url, '/')[:-1]
        headers = {'User-Agent': common.RAND_UA, 'Referer': web_url, 'Origin': origin}

        # The /v/<code> page is a Next.js app; the internal video UUID that the
        # playback API expects is only in the RSC flight data, next to publicId.
        page = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'"videoId":"([0-9a-f-]{36})"', page) \
            or re.search(r'\\"videoId\\":\\"([0-9a-f-]{36})\\"', page)
        if not r:
            raise ResolverError('File not found')
        video_uuid = r.group(1)

        # A playback session hands back the master URL plus a bearer token.
        # jdata=True lets net serialize the dict and set the JSON content type.
        api = urllib_parse.urljoin(web_url, '/api/playback/sessions')
        pdata = {'videoId': video_uuid, 'referrer': web_url, 'embedMode': True}
        session = self.net.http_POST(api, form_data=pdata, headers=headers, jdata=True).json
        stream_url = session.get('streamUrl')
        token = session.get('token')
        if not stream_url or not token:
            raise ResolverError('Unable to locate stream URL')

        # The master playlist (and the CDN redirect it triggers) needs the token
        # as a bearer header; child/segment URLs are relative to the redirected
        # CDN response, which already carries its own signature.
        stream_url = urllib_parse.urljoin(web_url, stream_url)
        play_headers = {'User-Agent': headers['User-Agent'],
                        'Referer': origin + '/',
                        'Authorization': 'Bearer {0}'.format(token)}
        return stream_url + helpers.append_headers(play_headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}')
