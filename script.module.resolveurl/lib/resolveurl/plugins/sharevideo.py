"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class ShareVideoResolver(ResolveUrl):
    name = 'ShareVideo'
    domains = ['sharevideo.pl']
    pattern = r'(?://|\.)(sharevideo\.pl)/(?:videos/embed|w)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': urllib_parse.urljoin(web_url, '/')
        }
        html = self.net.http_GET(web_url, headers=headers).content
        sources = json.loads(html).get('streamingPlaylists')
        if sources:
            url = sources[0].get('playlistUrl')
            # url = sources[0].get('files')[0].get('fileDownloadUrl')
            return url + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/api/v1/videos/{media_id}')
