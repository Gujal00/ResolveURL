'''
videobee resolveurl plugin
Copyright (C) 2016 Gujal

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
'''
import re
from urlparse import urlparse
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VideoBeeResolver(ResolveUrl):
    name = "thevideobee.to"
    domains = ["thevideobee.to"]
    pattern = '(?://|\.)(thevideobee\.to)/(?:embed-)?([0-9A-Za-z]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        packed = helpers.get_packed_data(html)
        
        try:
            sources = re.search("""sources:\s*\["(.+?)"\]""", packed).group(1).split('","')
            sources = [(urlparse(sources[i]).path.split('/')[-1], sources[i]) for i in range(len(sources))]
        except:
            sources = helpers.scrape_sources(html, patterns=["""sources:\s*\[["'](?P<url>[^"']+)"""])
        
        if sources:
            headers.update({'Referer': web_url})
            return helpers.pick_source(sources) + helpers.append_headers(headers)
        
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
