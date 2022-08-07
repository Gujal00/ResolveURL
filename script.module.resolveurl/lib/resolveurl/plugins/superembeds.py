"""
    Plugin for ResolveURL
    Copyright (C) 2022 gujal

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
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class SuperEmbedsResolver(ResolveUrl):
    name = 'SuperEmbeds'
    domains = ['superembeds.com']
    pattern = r'(?://|\.)(superembeds\.com)/embed(\d*/[0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        html += helpers.get_packed_data(html)
        r = re.search(r'FirePlayer\("([^"]+)', html)
        if r:
            fire_id = r.group(1)
            furl = 'https://{0}/player/index.php?data={1}&do=getVideo'.format(host, fire_id)
            form_data = {'hash': fire_id, 'r': ''}
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            resp = self.net.http_POST(furl, form_data, headers).content
            strurl = json.loads(resp).get('securedLink')
            if strurl:
                headers.pop('X-Requested-With')
                return strurl + helpers.append_headers(headers)

        raise ResolverError('File could not be located')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed{media_id}')
