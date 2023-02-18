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
from resolveurl.lib import helpers
from resolveurl.lib import captcha_lib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

MAX_TRIES = 3


class DropResolver(ResolveUrl):
    name = 'Drop'
    domains = ['drop.download']
    pattern = r'(?://|\.)(drop\.download)/([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        if 'File Not Found' not in html:
            data = helpers.get_hidden(html)
            data.update({"method_free": "Free Download >>"})
            headers.update({'Referer': web_url,
                            'Origin': 'https://{0}'.format(host)})
            html = self.net.http_POST(web_url, form_data=data, headers=headers).content
            tries = 0
            while tries < MAX_TRIES:
                data = helpers.get_hidden(html)
                data.update({"method_free": "Free Download >>"})
                data.update(captcha_lib.do_captcha(html))
                common.kodi.sleep(15000)
                html = self.net.http_POST(web_url, form_data=data, headers=headers).content
                r = re.search(r'''<a\s*href="([^"]+)"\s*class="btn-download''', html, re.DOTALL)
                if r:
                    # headers.update({'verifypeer': 'false'})
                    return r.group(1).replace(' ', '%20') + helpers.append_headers(headers)
                tries += 1
            raise ResolverError('Unable to locate link')

        raise ResolverError('File removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
