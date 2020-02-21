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
import xbmc

class MyviRuResolver(ResolveUrl):
    name = "myviru"
    domains = ["myvi.ru", "myvi.tv"]
    pattern = '(?://|\.)(myvi\.(?:ru|tv))/(?:\w+/)?(?:embed|watch)/?(?:\w+/)?([0-9a-zA-Z_-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content
        if isinstance(html, unicode): html = html.encode('utf-8', 'ignore')

        match = re.search('\"video\"\s*:\s*\[([^\]]+)\]', html, re.I | re.M | re.DOTALL)
        if not match:
            raise ResolverError('File Not Found or removed')

        json_loaded = json.loads(match.group(1))
        sources = [json_loaded.get('url') for i in json_loaded if json_loaded.get('url')][0]

        uuid = self.net.get_cookies(True)["UniversalUserID"]
		
        redirected_to = self.net.http_GET(sources, {'Cookie': 'UniversalUserID=%s' % uuid, 'User-Agent': common.RAND_UA}).get_url()

        return redirected_to + helpers.append_headers({'Cookie': 'UniversalUserID=%s' % uuid, 'User-Agent': common.RAND_UA})

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://myvi.ru/player/api/Video/Get/{media_id}?sig')
