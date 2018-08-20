"""
    putvid plugin for ResolveURL
    Copyright (C) 2018 gujal

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
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from lib import helpers

class PutVidResolver(ResolveUrl):
    name = "putvid"
    domains = ['putvid.com']
    pattern = '(?://|\.)(putvid\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
    
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        if html:
            sources = helpers.scrape_sources(html, patterns=['''sources:[^"]+"(?P<url>[^"]+)'''], generic_patterns=False)
            if sources:
                source = helpers.pick_source(sources)
                return source

        raise ResolverError('File not found')
