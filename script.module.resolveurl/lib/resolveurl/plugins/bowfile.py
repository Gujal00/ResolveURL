"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class BowFileResolver(ResolveUrl):
    name = 'BowFile'
    domains = ['bowfile.com']
    pattern = r'(?://|\.)(bowfile\.com)/(?:video/embed/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'Referer': web_url,
            'User-Agent': common.RAND_UA
        }
        response = self.net.http_GET(web_url, headers=headers)
        dl_url = re.search(r'let\s*next\s*=\s*"([^"]+)', response.content)
        cookie = response.get_headers(as_dict=True).get('Set-Cookie', '')
        if dl_url:
            headers.update({'Cookie': cookie.split(';')[0]})
            common.kodi.sleep(10000)
            url = self.net.http_GET(dl_url.group(1), headers=headers, redirect=False).get_redirect_url()
            if url and url != web_url:
                return url.replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
