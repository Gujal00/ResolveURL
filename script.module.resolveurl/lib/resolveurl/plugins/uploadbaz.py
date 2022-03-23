"""
    Plugin for ResolveUrl
    Copyright (C) 2022 shellc0de

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

from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class UploadBazResolver(ResolveUrl):
    name = 'uploadbaz'
    domains = ['uploadbaz.me']
    pattern = r'(?://|\.)(uploadbaz\.me)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net(ssl_verify=False)

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        r = self.net.http_GET(web_url, headers=headers)
        html = r.content
        if 'File Not Found' in html:
            raise ResolverError('File Removed')
        url = r.get_url()
        payload = helpers.get_hidden(html)
        headers.update({'Origin': web_url.rsplit('/', 1)[0], 'Referer': url})
        surl = self.net.http_POST(url, form_data=payload, headers=headers).get_url()
        if surl != url:
            headers.pop('Origin')
            headers.update({'verifypeer': 'false'})
            return surl.replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError('File Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/{media_id}')
