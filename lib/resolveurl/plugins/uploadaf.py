"""
grifthost resolveurl plugin
Copyright (C) 2015 tknorris

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
from lib import captcha_lib
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

MAX_TRIES = 3

class UploadAfResolver(ResolveUrl):
    name = "upload.af"
    domains = ["upload.af", "upload.mn"]
    pattern = '(?://|\.)(upload\.(?:af|mn))/([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        headers = {'User-Agent': common.RAND_UA, 'Referer': web_url}

        tries = 0
        while tries < MAX_TRIES:
            data = helpers.get_hidden(html, index=0)
            data.update(captcha_lib.do_captcha(html))

            html = self.net.http_POST(web_url, headers=headers, form_data=data).content
            match = re.search('href="([^"]+)[^>]*>Click here to download<', html, re.DOTALL | re.I)
            if match:
                return match.group(1) + helpers.append_headers(headers)
            tries += 1

        raise ResolverError('Unable to resolve uploadz.co link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'https://upload.mn/%s' % (media_id)
