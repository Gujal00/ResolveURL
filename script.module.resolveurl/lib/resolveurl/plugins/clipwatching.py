"""
    Plugin for ResolveUrl
    Copyright (C) 2019 gujal

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


class ClipWatchingResolver(ResolveUrl):
    name = "clipwatching"
    domains = ['clipwatching.com', 'highstream.tv']
    pattern = r'(?://|\.)((?:clipwatching\.com|highstream.tv))/(?:embed-)?(\w+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            _srcs = re.search(r'sources\s*:\s*\[(.+?)\]', html)
            if _srcs:
                srcs = helpers.scrape_sources(_srcs.group(1), patterns=['''["'](?P<url>http[^"']+)'''])
                if srcs:
                    headers.update({'Referer': web_url})
                    return helpers.pick_source(srcs) + helpers.append_headers(headers)

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
