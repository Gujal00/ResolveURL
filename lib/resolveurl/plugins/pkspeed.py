"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal

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

from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.plugins.lib import helpers


class PKSpeedResolver(ResolveUrl):
    name = "pkspeed.net"
    domains = ["pkspeed.net"]
    pattern = r'(?://|\.)(pkspeed\.net)/(?:embed-)?([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Cookie': 'ref_url=http%3A%2F%2Fwww.movieswatch.com.pk%2F',
                   'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.scrape_sources(html)
        if sources:
            headers.pop('Cookie')
            return helpers.pick_source(sources) + helpers.append_headers(headers)
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
