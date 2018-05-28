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

import re, base64
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class StreamMoeResolver(ResolveUrl):
    name = "streammoe"
    domains = ["stream.moe"]
    pattern = '(?://|\.)(stream\.moe)/(?:embed\d*/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        try: html = base64.b64decode(re.search('atob\(\'(.+?)\'', html).group(1))
        except: pass

        source_list = helpers.scrape_sources(html)
        source = helpers.pick_source(source_list)
        return source

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/{media_id}')
