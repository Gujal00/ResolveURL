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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class BitchuteResolver(ResolveUrl):

    name = 'Bitchute'
    domains = ['bitchute.com']
    pattern = r'(?://|\.)(bitchute\.com)/(?:video|embed)/([\w-]+)/'

    def get_media_url(self, host, media_id):
        api_url = 'https://api.bitchute.com/api/beta/video/media'
        payload = {"video_id": media_id}
        ref = urllib_parse.urljoin(self.get_url(host, media_id), '/')
        headers = {
            'User-Agent': common.RAND_UA,
            'Origin': ref[:-1],
            'Referer': ref
        }
        res = self.net.http_POST(api_url, form_data=payload, headers=headers, jdata=True).content
        if res:
            video = json.loads(res).get('media_url')
            return video + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.{host}/video/{media_id}')
