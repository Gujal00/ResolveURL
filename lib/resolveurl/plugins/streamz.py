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


class StreamzResolver(ResolveUrl):
    name = "streamz"
    domains = ['streamz.cc', "streamz.vg", "streamzz.to"]
    pattern = r'(?://|\.)(streamzz?\.(?:cc|vg|to))/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):

        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        html += helpers.get_packed_data(html)
        sources = helpers.scrape_sources(html)

        if sources:
            headers.update({'Referer': web_url})
            vurl = helpers.pick_source(sources)
            vurl = re.sub('get[a-zA-Z]{4}-', 'getlink-', vurl)
            vurl = re.sub('get[a-zA-Z]{5}-', 'getlink-', vurl)
            return helpers.get_redirect_url(vurl, headers) + helpers.append_headers(headers)

        raise ResolverError("Video not found")

    def get_url(self, host, media_id):

        return self._default_get_url(host, media_id, template='https://streamz.vg/{media_id}')
