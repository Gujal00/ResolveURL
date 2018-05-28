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

import re
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class AnimePortalResolver(ResolveUrl):
    name = "animeportal"
    domains = ["anime-portal.org"]
    pattern = '(?://|\.)(anime-portal\.org)/(?:embed/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        match = re.search('''cnf\s*=\s*['"]([^'"]+)''', html, re.I)
        if not match:
            raise ResolverError('File Not Found or removed')

        html = self.net.http_GET(match.group(1)).content

        sources = [(r.group(1).upper(), r.group(2)) for r in re.finditer('''<file(\w*)>(.*?)</file\w*>''', html, re.DOTALL)]
        sources = sorted(sources, key=lambda k: k[0], reverse=True)

        return helpers.pick_source(sources)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/embed/{media_id}')
