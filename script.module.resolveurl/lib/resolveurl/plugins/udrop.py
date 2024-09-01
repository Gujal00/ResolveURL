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


class UDropResolver(ResolveUrl):
    name = 'UDrop'
    domains = ['udrop.com']
    pattern = r'(?://|\.)(udrop\.com)/(?:video/embed/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://www.{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'showFileInformation\((\d+)', html)
        if r:
            data = {'u': r.group(1), 'p': 'true'}
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.{0}'.format(host)
            })
            res = self.net.http_POST('https://www.{0}/account/ajax/file_details'.format(host), data, headers).content
            s = re.search(r'''openUrl\('([^']+)''', res)
            if s:
                str_url = s.group(1).replace('\\/', '/')
                headers.pop('X-Requested-With')
                return str_url + helpers.append_headers(headers)

        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/{media_id}')
