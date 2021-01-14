"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class JetloadResolver(ResolveUrl):
    name = 'jetload'
    domains = ['jetload.net', 'jetload.to']
    pattern = r'(?://|\.)(jetload\.(?:net|tv|to))/(?:[a-zA-Z]/|.*?embed\.php\?u=)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        surl = 'https://jetload.net/jet_secure'
        domain = 'aHR0cHM6Ly9qZXRsb2FkLm5ldDo0NDM.'
        web_url = self.get_url(host, media_id)
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers).content
        if 'File Deleted' not in html:
            token = helpers.girc(html, rurl, domain)
            if token:
                edata = {'stream_code': media_id,
                         'token': token}
                headers.update({'Origin': rurl[:-1]})
                shtml = self.net.http_POST(surl, form_data=edata, headers=headers, jdata=True).content
                r = re.search('"src":"([^"]+)', shtml)
                if r:
                    return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')
