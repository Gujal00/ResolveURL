"""
    plugin for ResolveURL
    Copyright (C) 2020 gujal

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
import random
import string
import time
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class DoodStreamResolver(ResolveUrl):
    name = "doodstream"
    domains = ['dood.watch', 'doodstream.com', 'dood.to']
    pattern = r'(?://|\.)(dood(?:stream)?\.(?:com|watch|to))/(?:d|e)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}

        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'''dsplayer\.hotkeys[^']+'([^']+).+?function\s*makePlay.+?return[^?]+([^"]+)''', html, re.DOTALL)
        if match:
            token = match.group(2)
            url = 'https://dood.to' + match.group(1)
            headers.update({'Referer': web_url})
            html = self.net.http_GET(url, headers=headers).content
            return self.dood_decode(html) + token + str(int(time.time() * 1000)) + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://dood.to/e/{media_id}')

    def dood_decode(self, data):
        t = string.ascii_letters + string.digits
        return data + ''.join([random.choice(t) for _ in range(10)])
