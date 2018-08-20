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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class Mp4streamResolver(ResolveUrl):
    name = "mp4stream"
    domains = ["mp4stream.com"]
    pattern = '(?://|\.)(mp4stream\.com)/embed/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.EDGE_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        url = re.findall('src\s*:\s*\'(.+?)\'', html)
        if url:
            return url[-1] + helpers.append_headers(headers)
        else:
            raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://mp4stream.com/embed/%s' % media_id
