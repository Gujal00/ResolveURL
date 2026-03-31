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
from resolveurl import common
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric

api_url = 'https://api.bitchute.com/api/beta/video/media'


class BitchuteResolver(ResolveGeneric):

    name = 'Bitchute'
    domains = ['bitchute.com']
    pattern = r'(?://|\.)(bitchute\.com)/(?:video|embed)/([\w-]+)/'

    def get_media_url(self, host, media_id):

        payload = {"video_id": media_id}

        headers = {
            'User-Agent': common.RAND_UA, 'Content-Type': 'application/json',
            'Origin': 'https://www.bitchute.com', 'Referer': 'https://www.bitchute.com/'
        }

        res = self.net.http_POST(api_url, form_data=payload, headers=headers, jdata=True).content

        video = json.loads(res)

        return video.get('media_url')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.{host}/video/{media_id}')
