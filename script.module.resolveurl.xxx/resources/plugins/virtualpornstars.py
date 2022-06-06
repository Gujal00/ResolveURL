"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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
import sys
from six.moves import urllib_request
import ssl
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VirtualPornStarsResolver(ResolveUrl):
    name = 'virtualpornstars'
    domains = ['virtualpornstars.com']
    pattern = r'(?://|\.)(virtualpornstars\.com)/(?:\w+/)?([\w\-]+)'

    def __init__(self):
        if sys.version_info < (2, 7, 9):
            raise ResolverError('Python 2.7.9 or greater required')
        self.context = ssl._create_unverified_context()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        request = urllib_request.Request(web_url, headers=headers)
        response = urllib_request.urlopen(request, context=self.context)
        html = response.read()
        source = re.search(r'''file:\s*["']([^"']+)''', html)
        if source:
            headers.update({'Referer': web_url})
            return source.group(1) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return False if sys.version_info < (2, 7, 9) else True
