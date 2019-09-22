"""
    ResolveURL Kodi module
    VlareTV plugin
    Copyright (C) 2019 twilight0

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
from resolveurl.resolver import ResolveUrl
from lib import helpers
from resolveurl import common


class VlareTVResolver(ResolveUrl):

    name = "vlare.tv"
    domains = ['vlare.tv']
    pattern = r'(?://|\.)(vlare\.tv)/(?:v|embed)/([\w-]+)(?:/(?:false|true)/(?:false|true)/\d+?)?'

    def __init__(self):

        self.net = common.Net()
        self.headers = {'User-Agent': common.RAND_UA}

    def get_media_url(self, host, media_id):

        web_url = self.get_url(host, media_id)
        res = self.net.http_GET(web_url, headers=self.headers)

        sources = re.findall(
            '''["']file["']:["'](?P<url>https?.+?\.mp4)["'],["']label["']:["'](\d{3,4}p)["']''',
            res.content
        )

        sources = [(s[1], s[0]) for s in sources]

        return helpers.pick_source(sources)

    def get_url(self, host, media_id):

        return self._default_get_url(host, media_id, 'https://{host}/embed/{media_id}')
