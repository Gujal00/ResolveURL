"""
    ResolveUrl Plugin
    Copyright (C) 2017 Gujal

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
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError

class VideoHost2Resolver(ResolveUrl):
    name = 'videohost2.com'
    domains = ['videohost2.com']
    pattern = '(?://|\.)(videohost2\.com)/playh\.php\?id=([0-9a-f]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        r = re.search("atob\('([^']+)", html)

        if r:
            stream_page = r.group(1).decode('base64')
            r2 = re.search("source\s*src='([^']+)", stream_page)
            if r2:
                stream_url = r2.group(1)
            else:
                raise ResolverError('no file located')
        else:
            raise ResolverError('no file located')

        return stream_url + helpers.append_headers({'User-Agent': common.FF_USER_AGENT})

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/playh.php?id={media_id}')
