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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VodLockResolver(ResolveUrl):
    name = "vodlock"
    domains = ['vodlock.co']
    pattern = '(?://|\.)(vodlock\.co)/(?:embed-)?([a-zA-Z0-9]+)'
    
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        _html = self.net.http_GET(web_url, headers=headers).content
        data = helpers.get_hidden(_html)
        headers.update({'Referer': web_url})
        common.kodi.sleep(3000)
        html = self.net.http_POST(web_url, headers=headers, form_data=data).content
        
        if html:
            packed = helpers.get_packed_data(html)
            _sources = re.search("""sources:\s*\[([^\]]+)""", packed)
            if _sources:
                sources = re.findall("""["']([^"'\s,]+)""", _sources.group(1))
                if sources:
                    from urlparse import urlparse
                    sources = [(urlparse(source).path.split('/')[-1], source) for source in sources]
                    return helpers.pick_source(sources) + helpers.append_headers(headers)
            
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/{media_id}')
