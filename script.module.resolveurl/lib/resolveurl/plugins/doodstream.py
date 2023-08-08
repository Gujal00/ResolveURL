"""
    Plugin for ResolveURL
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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class DoodStreamResolver(ResolveUrl):
    name = 'DoodStream'
    domains = ['dood.watch', 'doodstream.com', 'dood.to', 'dood.so', 'dood.cx', 'dood.la', 'dood.ws',
               'dood.sh', 'doodstream.co', 'dood.pm', 'dood.wf', 'dood.re', 'dood.yt', 'dooood.com',
               'dood.stream', 'ds2play.com', 'doods.pro']
    pattern = r'(?://|\.)((?:do*ds?(?:tream)?|ds2play)\.' \
              r'(?:com?|watch|to|s[ho]|cx|la|w[sf]|pm|re|yt|stream|pro))/(?:d|e)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        if any(host.endswith(x) for x in ['.cx', '.wf']):
            host = 'dood.so'
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://{0}/'.format(host)}

        r = self.net.http_GET(web_url, headers=headers)
        if r.get_url() != web_url:
            host = re.findall(r'(?://|\.)([^/]+)', r.get_url())[0]
            web_url = self.get_url(host, media_id)
        headers.update({'Referer': web_url})
        html = r.content

        match = re.search(r'<iframe\s*src="([^"]+)', html)
        if match:
            url = 'https://{0}{1}'.format(host, match.group(1))
            html = self.net.http_GET(url, headers=headers).content
        else:
            url = web_url.replace('/d/', '/e/')
            html = self.net.http_GET(url, headers=headers).content

        match = re.search(r'''dsplayer\.hotkeys[^']+'([^']+).+?function\s*makePlay.+?return[^?]+([^"]+)''', html, re.DOTALL)
        if match:
            token = match.group(2)
            url = 'https://{0}{1}'.format(host, match.group(1))
            html = self.net.http_GET(url, headers=headers).content
            return self.dood_decode(html) + token + str(int(time.time() * 1000)) + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/d/{media_id}')

    def dood_decode(self, data):
        t = string.ascii_letters + string.digits
        return data + ''.join([random.choice(t) for _ in range(10)])
