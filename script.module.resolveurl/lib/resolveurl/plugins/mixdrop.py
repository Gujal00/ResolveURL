"""
    Plugin for ResolveURL
    Copyright (C) 2019 gujal

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
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib import helpers


class MixDropResolver(ResolveUrl):
    name = 'MixDrop'
    domains = ['mixdrop.co', 'mixdrop.to', 'mixdrop.sx', 'mixdrop.bz', 'mixdrop.ch',
               'mixdrp.co', 'mixdrp.to', 'mixdrop.gl', 'mixdrop.club']
    pattern = r'(?://|\.)(mixdro?p\.(?:c[ho]|to|sx|bz|gl|club))/(?:f|e)/(\w+)'

    def get_media_url(self, host, media_id):
        if host.endswith('.club'):
            host = host.replace('.club', '.co')
        web_url = self.get_url(host, media_id)
        rurl = 'https://{}/'.format(host)
        headers = {'Origin': rurl[:-1],
                   'Referer': rurl,
                   'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'location\s*=\s*"([^"]+)', html)
        if r:
            web_url = 'https://{0}{1}'.format(host, r.group(1))
            html = self.net.http_GET(web_url, headers=headers).content
        if '(p,a,c,k,e,d)' in html:
            html = helpers.get_packed_data(html)
        r = re.search(r'(?:vsr|wurl|surl)[^=]*=\s*"([^"]+)', html)
        if r:
            surl = r.group(1)
            if surl.startswith('//'):
                surl = 'https:' + surl
            headers.pop('Origin')
            headers.update({'Referer': web_url})
            return surl + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
