"""
    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
import urlparse
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class YourUploadResolver(ResolveUrl):
    name = "yourupload.com"
    domains = ["yourupload.com", "yucache.net"]
    pattern = '(?://|\.)(yourupload\.com|yucache\.net)/(?:watch|embed)?/?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content
        url = re.findall('file\s*:\s*(?:\'|\")(.+?)(?:\'|\")', html)

        if not url: raise ResolverError('No video found')

        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}

        url = urlparse.urljoin(web_url, url[0])
        url = self.net.http_HEAD(url, headers=headers).get_url()

        url = url + helpers.append_headers(headers)
        return url

        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return 'http://www.yourupload.com/embed/%s' % media_id
