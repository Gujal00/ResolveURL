"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class YouPornResolver(ResolveUrl):
    name = 'youporn'
    domains = ['youporn.com']
    pattern = r'(?://|\.)(youporn\.com)/(?:watch|embed)/(\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'Referer': 'https://www.{}/'.format(host),
            'User-Agent': common.RAND_UA
        }
        r = self.net.http_GET(web_url, headers=headers)
        jdata = json.loads(r.content)
        sources = [(x.get('quality'), x.get('videoUrl')) for x in jdata]
        if sources:
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/api/video/media_definitions/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
