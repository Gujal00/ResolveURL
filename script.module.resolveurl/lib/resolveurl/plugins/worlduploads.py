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
from resolveurl.lib import helpers
from resolveurl.lib import captcha_lib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from six.moves import urllib_parse

MAX_TRIES = 3


class WorldUploadsResolver(ResolveUrl):
    name = 'WorldUploads'
    domains = ['worlduploads.com']
    pattern = r'(?://|\.)(worlduploads\.com)/([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        if 'File Not Found' not in html:
            tries = 0
            while tries < MAX_TRIES:
                data = helpers.get_hidden(html)
                data.update({
                    'method_free': '',
                    'method_premium': '',
                    'adblock_detected': 0
                })
                data.update(captcha_lib.do_captcha(html))
                common.kodi.sleep(30000)
                headers.update({'Referer': web_url,
                                'Origin': urllib_parse.urljoin(web_url, '/')[:-1]})
                html = self.net.http_POST(web_url, data, headers=headers).content
                r = re.search(r'class="filepanel.+?href="([^"]+)', html, re.DOTALL)
                if r:
                    return urllib_parse.quote(r.group(1), '/:') + helpers.append_headers(headers)

                common.kodi.sleep(2000)
                tries = tries + 1
            raise ResolverError('Unable to locate link')
        else:
            raise ResolverError('File deleted')
        return

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @classmethod
    def isPopup(self):
        return True
