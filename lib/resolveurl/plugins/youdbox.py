"""
    Plugin for ResolveUrl
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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class YouDBoxResolver(ResolveUrl):
    name = "youdbox"
    domains = ['youdbox.com']
    pattern = r'(?://|\.)(youdbox\.com)/(?:embed-)?(\w+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url).content
        r = re.search(r"{var\s*[^\s]+\s*=\s*(\[[^\]]+])", html)

        if r:
            data = eval(r.group(1))
            data = ''.join(data[::-1])
            s = re.search(r'source\s*src="([^"]+)', data)
            if s:
                url = s.group(1) + helpers.append_headers(headers)
                return url

        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
