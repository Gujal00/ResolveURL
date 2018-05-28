"""
streamcloud resolveurl plugin
Copyright (C) 2012 Lynx187

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

import re
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamcloudResolver(ResolveUrl):
    name = "streamcloud"
    domains = ["streamcloud.eu"]
    pattern = '(?://|\.)(streamcloud\.eu)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        if re.search('>(File Not Found)<', html):
            raise ResolverError('File Not Found or removed')

        cnt = 10
        match = re.search('count\s*=\s*(\d+);', html)
        if match:
            cnt = int(match.group(1))
        cnt += 1

        data = helpers.get_hidden(html)
        headers.update({'Referer': web_url})
        common.kodi.sleep(cnt * 1000)
        html = self.net.http_POST(response.get_url(), form_data=data, headers=headers).content
        sources = helpers.scrape_sources(html, patterns=['''file\s*:\s*["'](?P<url>[^"']+)'''])
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://streamcloud.eu/%s' % (media_id)
