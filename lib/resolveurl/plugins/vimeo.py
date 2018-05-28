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
import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VimeoResolver(ResolveUrl):
    name = "vimeo"
    domains = ["vimeo.com"]
    pattern = '(?://|\.)(vimeo\.com)/(?:video/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': 'https://vimeo.com/', 'Origin': 'https://vimeo.com'}
        data = self.net.http_GET(web_url, headers).content
        data = json.loads(data)
        sources = [(vid['height'], vid['url']) for vid in data.get('request', {}).get('files', {}).get('progressive', {})]
        try: sources.sort(key=lambda x: x[0], reverse=True)
        except: pass
        return helpers.pick_source(sources)

    def get_url(self, host, media_id):
        return 'https://player.vimeo.com/video/%s/config' % media_id
