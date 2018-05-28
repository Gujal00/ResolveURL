"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

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
import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class PlayWireResolver(ResolveUrl):
    name = "playwire"
    domains = ["playwire.com"]
    pattern = '(?://|\.)(config\.playwire\.com)/(.+?)/(?:zeus|player)\.json'
    pattern2 = '(?://|\.)(cdn\.playwire\.com.+?\d+)/(?:config|embed)/(\d+)'
    qual_map = {'1080': 'Full HD', '720': "HD", '480': "SD", '360': 'Low Quality', '270': 'Poor Quality', '240': 'Mobile HD', '144': 'Mobile SD'}

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content

        if html:
            try:
                if 'config.playwire.com' in host:
                    response = json.loads(html)['content']['media']['f4m']
                elif 'v2' not in host:
                    response = re.findall(r'<src>(.+?)</src>', html)[0]
                else:
                    response = json.loads(html)['src']
                    return response

                response = self.net.http_GET(response).content
                baseURL = re.findall(r'<baseURL>\s*(.+)\s*</baseURL>', response)[0]
                media = re.findall(r'<media url="(\S+)".+?height="(\d+)".*?/>', response)
                media.sort(key=lambda x: x[1], reverse=True)
                sources = [('%s' % self.__replaceQuality(i[1], i[1]), '%s/%s' % (baseURL, i[0])) for i in media]
                source = helpers.pick_source(sources)
                source = source.encode('utf-8')

                return source

            except:
                raise ResolverError('Unable to resolve url.')

        raise ResolverError('No playable video found.')

    def __replaceQuality(self, qual, num):
        return self.qual_map.get(qual, num)

    def get_url(self, host, media_id):
        if 'config.playwire.com' in host:
            return 'http://%s/%s/zeus.json' % (host, media_id)
        elif 'v2' not in host:
            return 'http://%s/embed/%s.xml' % (host, media_id)
        else:
            return 'http://%s/config/%s.json' % (host, media_id)

    def get_host_and_id(self, url):
        if 'config.playwire.com' in url: r = re.search(self.pattern, url)
        else: r = re.search(self.pattern2, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or re.search(self.pattern2, url) or self.name in host
