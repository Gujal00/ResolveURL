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
from resolveurl.lib import helpers, captcha_lib
from resolveurl.resolver import ResolveUrl, ResolverError


class UploadingSiteResolver(ResolveUrl):
    name = 'UploadingSite'
    domains = ['uploadingsite.com', 'uploadingsite.info']
    pattern = r'(?://|\.)(uploadingsite\.(?:com|info))/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        payload = helpers.get_hidden(html)
        if not payload:
            raise ResolverError('File Removed')

        common.kodi.sleep(5000)
        payload.update(captcha_lib.do_captcha(html))
        headers.update({'Origin': web_url.rsplit('/', 1)[0], 'Referer': web_url})
        html = self.net.http_POST(web_url, form_data=payload, headers=headers).content
        url = re.search(r'href="([^"]+).+?>\s*Download', html)
        if url:
            headers['verifypeer'] = 'false'
            return url.group(1).replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError('File Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
