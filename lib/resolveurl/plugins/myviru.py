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

import re, json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class MyviRuResolver(ResolveUrl):
    name = "myviru"
    domains = ["myvi.ru"]
    pattern = '(?://|\.)(myvi\.ru)/(?:\w+/)?(?:embed|watch)/?(?:\w+/)?([0-9a-zA-Z_-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content
        if isinstance(html, unicode): html = html.encode('utf-8', 'ignore')

        match = re.search('''['"]video['"]\s*:\s*(\[[^\]]+\])''', html, re.I | re.M | re.DOTALL)
        if not match:
            raise ResolverError('File Not Found or removed')

        sources = [i.get('url') for i in json.loads(match.group(1)) if i.get('url')][0]

        uuid = self.net.get_cookies().get('.'+host).get('/').get('UniversalUserID').value

        return sources + helpers.append_headers({'Cookie': 'UniversalUserID=%s' % uuid, 'User-Agent': common.RAND_UA})

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/player/api/Video/Get/{media_id}?sig')
