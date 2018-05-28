'''
    resolveurl Kodi plugin
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
'''

from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import re

class GoFlickerResolver(ResolveUrl):
    name = "goflicker.com"
    domains = ["goflicker.com"]
    pattern = '(?://|\.)(goflicker\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        if 'Not Found' in html:
            raise ResolverError('File Removed')

        if 'Video is processing' in html:
            raise ResolverError('File still being processed')

        strurl = re.findall('sources.*"(.*?)"',html)[0]
        return strurl + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
