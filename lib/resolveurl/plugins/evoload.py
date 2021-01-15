"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class EvoLoadResolver(ResolveUrl):
    name = "evoload"
    domains = ["evoload.io"]
    pattern = r'(?://|\.)(evoload\.io)/(?:e|f|v)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        surl = 'https://evoload.io/SecurePlayer'
        domain = 'aHR0cHM6Ly9ldm9sb2FkLmlvOjQ0Mw..'
        web_url = self.get_url(host, media_id)
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers).content
        token = helpers.girc(html, rurl, domain)
        if token:
            edata = {'code': media_id,
                     'token': token}
            headers.update({'Origin': rurl[:-1],
                            'X-XSRF-TOKEN': ''})
            shtml = self.net.http_POST(surl, form_data=edata, headers=headers, jdata=True).content
            r = re.search('"src":"([^"]+)', shtml)
            if r:
                headers.pop('X-XSRF-TOKEN')
                return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
