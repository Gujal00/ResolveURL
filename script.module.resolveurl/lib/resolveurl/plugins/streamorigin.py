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

from six.moves import urllib_parse, urllib_error
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamOriginResolver(ResolveUrl):
    name = 'StreamOrigin'
    domains = ['embedorigin.cc']
    pattern = r'(?://|\.)(embedorigin\.cc)/e/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': urllib_parse.urljoin(web_url, '/')
        }
        # the embed page is a client side app, its player gets the signed links from the play api
        api_url = 'https://{0}/app/v1/play/{1}?embed=1'.format(host, media_id)
        try:
            data = self.net.http_GET(api_url, headers=headers).json
        except urllib_error.HTTPError:
            # removed files and unknown ids get a 404 with {"message":"No file"}
            raise ResolverError('File Not Found or Removed')
        # keep the master playlist: the audio is a separate rendition, the video playlist alone is silent
        src = data.get('hls')
        if src:
            return src + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
