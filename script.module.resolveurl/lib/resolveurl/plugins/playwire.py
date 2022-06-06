"""
    Plugin for ResolveURL
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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class PlayWireResolver(ResolveUrl):
    name = 'PlayWire'
    domains = ['playwire.com']
    pattern = r'(?://|\.)(config\.playwire\.com)/(.+?)/(?:zeus|player)\.json'
    pattern2 = r'(?://|\.)(cdn\.playwire\.com.+?\d+)/(?:config|embed)/(\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content

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
            media = re.findall(r'<media\s*url="(\S+mp4)".+?height="(\d+)"', response)
            media.sort(key=lambda x: x[1], reverse=True)
            sources = [(i[1], '{0}/{1}'.format(baseURL, i[0])) for i in media]
            source = helpers.pick_source(sources)
            source = source.encode('utf-8') if helpers.PY2 else source
            return source

        except:
            raise ResolverError('Unable to resolve url.')

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        if 'config.playwire.com' in host:
            return 'http://%s/%s/zeus.json' % (host, media_id)
        elif 'v2' not in host:
            return 'http://%s/embed/%s.xml' % (host, media_id)
        else:
            return 'http://%s/config/%s.json' % (host, media_id)

    def get_host_and_id(self, url):
        if 'config.playwire.com' in url:
            r = re.search(self.pattern, url)
        else:
            r = re.search(self.pattern2, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or re.search(self.pattern2, url) or self.name in host
