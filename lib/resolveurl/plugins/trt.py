'''
vidzi resolveurl plugin
Copyright (C) 2014 Eldorado

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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import re

class trtResolver(ResolveUrl):
    name = "trt"
    domains = ["trt.pl"]
    pattern = '(?://|\.)(trt\.pl)/(?:film)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}

        html = self.net.http_GET(web_url, headers=headers).content
        pages = re.findall('href="([^"]+)[^>]+class="mainPlayerQualityHref"[^>]+>(.*?)</a>', html)
        if pages:
            try: pages.sort(key=lambda x: int(x[1][:-1]), reverse=True)
            except: pass
            html = self.net.http_GET('https://www.trt.pl' + pages[0][0], headers=headers).content
        
        sources = helpers.scrape_sources(html, scheme='https')
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'https://www.trt.pl/film/%s' % media_id
