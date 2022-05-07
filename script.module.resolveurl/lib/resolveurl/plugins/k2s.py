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

import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class K2SResolver(ResolveUrl):
    name = "K2S"
    domains = ["k2s.cc", "publish2.me", "tezfiles.com"]
    pattern = r'(?://|\.)(k2s\.cc|publish2\.me|tezfiles\.com)/(?:file/)?([0-9a-f]+)'

    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        api_base = 'https://api.k2s.cc/v1'
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': url,
                   'Origin': 'https://k2s.cc'}
        data = {"grant_type": "client_credentials",
                "client_id": "k2s_web_app",
                "client_secret": "pjc8pyZv7vhscexepFNzmu4P"}
        t = self.net.http_POST(api_base + '/auth/token', form_data=data, headers=headers, jdata=True).content
        access_token = json.loads(t).get('access_token')
        headers.update({'Authorization': 'Bearer {0}'.format(access_token)})
        s = self.net.http_GET('{0}/files/{1}?embed=permanentAbuse'.format(api_base, media_id), headers=headers).content
        s = json.loads(s)
        if 'video' not in s.get('contentType'):
            raise ResolverError('The requested file is not a video file.')
        videourl = s.get('videoPreview', {}).get('video')
        if videourl:
            headers.pop('Authorization')
            return videourl + helpers.append_headers(headers)
        raise ResolverError('The requested video was not found or may have been removed.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/preview/{media_id}')
