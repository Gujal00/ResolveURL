# -*- coding: utf-8 -*-

"""
Teramixer.com resolveurl XBMC Addon
Copyright (C) 2014 JUL1EN094 

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
import base64
import urllib
from resolveurl import common
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError

class TeramixerResolver(ResolveUrl):
    name = "teramixer"
    domains = ['teramixer.com']
    pattern = '(?://|\.)(teramixer\.com)/(?:embed/|)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        try:
            web_url = self.get_url(host, media_id)

            html = self.net.http_GET(web_url).content

            url = re.findall("""filepath = '(.*)';""", html)[0]
            url = url[9:]
            url = base64.b64decode(url)
            if not url.startswith('aws'): url = url[1:]

            stream_url = 'http://%s' % url + helpers.append_headers({'User-Agent': common.EDGE_USER_AGENT})
            return stream_url
        except IndexError as e:
            if re.search("""<title>File not found or deleted - Teramixer</title>""", html):
                raise ResolverError('File not found or removed')
            else:
                raise ResolverError(e)

    def get_url(self, host, media_id):
        return 'http://www.teramixer.com/%s' % media_id
