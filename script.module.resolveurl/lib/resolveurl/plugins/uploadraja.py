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

MAX_TRIES = 3


class UploadRajaResolver(ResolveUrl):
    name = 'UploadRaja'
    domains = ['uploadraja.com']
    pattern = r'(?://|\.)(uploadraja\.com)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url}
        r = self.net.http_GET(web_url, headers=headers)
        if web_url != r.get_url():
            web_url = r.get_url()
        html = r.content
        if 'File Not Found' not in html:
            tries = 0
            while tries < MAX_TRIES:
                payload = helpers.get_hidden(html)
                payload.update(captcha_lib.do_captcha(html))
                common.kodi.sleep(3000)
                html = self.net.http_POST(web_url, headers=headers, form_data=payload).content
                source = re.search(r'id="direct_link".+?href="([^"]+)', html, re.DOTALL)
                if source:
                    return source.group(1).replace(' ', '%20') + helpers.append_headers(headers)

                common.kodi.sleep(8000)
                tries = tries + 1
        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
