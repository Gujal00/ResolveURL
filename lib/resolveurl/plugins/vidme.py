"""
thevideo resolveurl plugin
Copyright (C) 2014 Eldorado
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

class VidMeResolver(ResolveUrl):
    name = "vid.me"
    domains = ["vid.me"]
    pattern = '(?://|\.)(vid\.me)/(?:embedded/|e/)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            sources = re.search('''data-sources\s*=\s*["']([^"']+)''', html)
            if sources:
                sources = sources.group(1).replace('&quot;', '"').replace('\/', '/')
                source = re.search('''"src":"([^"]+)","type":"application/x-mpegURL"''', sources)
                if source:
                    headers.update({"Referer": web_url})
                    source = source.group(1)
                    return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/embedded/{media_id}')
