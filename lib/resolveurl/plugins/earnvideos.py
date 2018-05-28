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

class EarnVideosResolver(ResolveUrl):
    name = "earnvideos"
    domains = ["earnvideos.com"]
    pattern = '(?://|\.)(earnvideos\.com)/(?:embed|thumb)/([a-zA-Z0-9\-]+)'

    def __init__(self):
        self.net = common.Net()
        self.UA = common.RAND_UA
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': self.UA}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            url = re.search('''url:\s*["']([^"']+)''', html)
            token = re.search('''<meta name=["']csrf-token["'] content=["']([^"']+)''', html)
            if url and token:
                url = web_url + url.group(1)
                token = token.group(1)
                headers.update({'Referer': web_url, 'x-csrf-token': token, 'x-requested-with': 'XMLHttpRequest', 'authority': host})
                _html = self.net.http_POST(url, form_data={'type': 'directLink'}, headers=headers).content
                if _html:
                    sources = helpers.scrape_sources(_html)
                    if sources: return helpers.pick_source(sources) + helpers.append_headers({'User-Agent': self.UA})
                    
        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
