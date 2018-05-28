"""
    Kodi resolveurl plugin
    Copyright (C) 2016  script.module.resolveurl

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
import string
from random import choice
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class MycloudResolver(ResolveUrl):
    name = "mycloud"
    domains = ["mycloud.to", "mcloud.to"]
    pattern = '(?://|\.)(my?cloud\.to)/embed/([\S]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA, 'Referer': 'https://www1.putlockertv.se/'}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            sources = helpers.scrape_sources(html)
            if sources:
                headers.update({'Referer': web_url})
                return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError("Unable to locate video")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://mcloud.to/embed/{media_id}?ui=%s' % ''.join(
            choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(24)))
