"""
    Kodi resolveurl plugin
    Copyright (C) 2017 alifrezser
    
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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class KingvidResolver(ResolveUrl):
    name = "kingvid"
    domains = ["kingvid.tv"]
    pattern = '(?://|\.)(kingvid\.tv)/(?:embed-)?([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        data = helpers.get_hidden(html)
        headers.update({'Referer': web_url})
        html = self.net.http_POST(web_url, headers=headers, form_data=data).content
        
        if html:
            sources = helpers.scrape_sources(html, patterns=['''file:["'](?P<url>[^"']+)'''], result_blacklist=['dl', '.smil'])
        
            return helpers.pick_source(sources) + helpers.append_headers(headers)
            
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
