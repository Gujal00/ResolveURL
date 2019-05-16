"""
    Kodi resolveurl plugin
    Copyright (C) 2019  script.module.resolveurl
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
# Updates:
# - 2019 05 12
# Old  vidtodo.me  vidotodo.com

from urlparse import urlparse
from lib import helpers
from resolveurl.common import Net, RAND_UA
from resolveurl.resolver import ResolveUrl, ResolverError


class VidToDoResolver(ResolveUrl):
    name = 'Vidtodo'
    domains = ['vidtodoo.com', 'vidtodo.com']
    pattern = '(?://|\.)((?:vidtodoo|vidtodo)\.(?:com))/(?:embed-)?([0-9a-zA-Z]+)'
 
    def __init__(self):
        self.net = Net()
        self.userAgent = RAND_UA
        self.net.set_user_agent(self.userAgent)
        self.desktopHeaders = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        }

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        r = self.net.http_GET(web_url, headers=self.desktopHeaders)

        sources = helpers.scrape_sources(
            r.content,
            generic_patterns=False,
            patterns=[
                '''sources.*?\[['"](?P<url>.*?)['"]''',
                '''sources.*?file:.*?['"](?P<url>.*?)['"](?:.*?label.*?['"](?P<label>.*?)['"])?''',
                '''updateSrc.*?src:.*?['"](?P<url>.*?)['"](?:.*?label.*?['"](?P<label>.*?)['"])?'''
            ]
        )
        if sources:
            # Headers for requesting media (copied from Firefox).
            parsedUrl = urlparse(r.get_url())
            kodiHeaders = {
                'User-Agent': self.userAgent,
                'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
                'Referer': '%s://%s/' % (parsedUrl.scheme, parsedUrl.netloc),
                'Cookie': '; '.join(cookie.name + '=' + cookie.value for cookie in self.net._cj)
            }
            return helpers.pick_source(sources) + helpers.append_headers(kodiHeaders)

        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
