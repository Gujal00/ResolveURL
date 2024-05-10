"""
    Plugin for ResolveURL
    Copyright (C) 2024 peter3344

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class QiwiResolver(ResolveUrl):
    name = 'Qiwi'
    domains = ['qiwi.gg']
    pattern = r'(?://|\.)(qiwi\.gg)/(?:file/)([^/\?]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Origin': 'https://{0}'.format(host),
                   'Referer': web_url
                   }
       
        html = self.net.http_GET(web_url, headers=headers).content
        
        r = re.search(r'class="page_TextHeading__VsM7r">([^"]+)</h1>', html)
        if r:
            ext = r.group(1).split('.')[-1]
            source = f"https://spyderrock.com/{media_id}.{ext}"
            return source + helpers.append_headers(headers)
        raise ResolverError('File Not Found or removed')
    
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/file/{media_id}')
