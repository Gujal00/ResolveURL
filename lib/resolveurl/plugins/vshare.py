"""
    vshare resolver for ResolveURL
    Copyright (C) 2018 holisticdioxide

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
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from lib import jsunpack, helpers

class VshareResolver(ResolveUrl):
    name = "vshare"
    domains = ['vshare.io']
    pattern = '(?://|\.)(vshare\.io)/\w?/(\w+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        js = jsunpack.unpack(html).split(';')
        try:
            charcodes = [int(val) for val in js[1].split('=')[-1].replace('[', '').replace(']', '').split(',')]
            sub = int(''.join(char for char in js[2].split('-')[1] if char.isdigit()))
        except IndexError:
            raise ResolverError('Video not found')
        charcodes = [val-sub for val in charcodes]
        try:
            srcs = ''.join(map(unichr, charcodes))
        except ValueError:
            raise ResolverError('Video not found')
        source_list = helpers.scrape_sources(srcs)
        source = helpers.pick_source(source_list)
        return source + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/v/{media_id}/width-750/height-400/')
