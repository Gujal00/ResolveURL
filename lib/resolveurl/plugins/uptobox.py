"""
    plugin for ResolveURL
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
import re
import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class UpToBoxResolver(ResolveUrl):
    name = "uptobox"
    domains = ["uptobox.com", "uptostream.com"]
    pattern = r'(?://|\.)(uptobox.com|uptostream.com)/(?:iframe/)?([0-9A-Za-z_]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if 'Not Found' in html:
            raise ResolverError('File Removed')

        packed = re.search(r"atob\('([^']+)", html)
        if packed:
            vidurl = json.loads(packed.group(1).decode('base64'))[0].get('src')
            return vidurl + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://uptostream.com/iframe/{media_id}')
