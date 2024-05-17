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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.lib import captcha_lib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class DailyUploadsResolver(ResolveUrl):
    name = 'DailyUploads'
    domains = ['dailyuploads.net']
    pattern = r'(?://|\.)(dailyuploads\.net)/([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        if 'File Not Found' not in html:
            data = helpers.get_hidden(html)
            data.update(captcha_lib.do_captcha(html))
            html = self.net.http_POST(web_url, data, headers=headers).content
            r = re.search(r'<td.+?href="([^"]+)', html)
            if r:
                return urllib_parse.quote(r.group(1), '/:') + helpers.append_headers(headers)

        raise ResolverError('File deleted')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @classmethod
    def isPopup(self):
        return True
