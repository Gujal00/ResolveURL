"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de

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


class MVidooResolver(ResolveUrl):
    name = 'MVidoo'
    domains = ['mvidoo.com']
    pattern = r'(?://|\.)(mvidoo\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'{var\s*[^\s]+\s*=\s*(\[[^\]]+])', html)
        if r:
            data = eval(r.group(1))
            data = ''.join(data[::-1])
            s = re.search(r'source\s*src="([^"]+)', data)
            if s:
                headers.update({'Referer': 'https://{}/'.format(host)})
                url = s.group(1) + helpers.append_headers(headers)
                return url

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
