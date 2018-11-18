'''
clicknupload resolveurl plugin
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
'''
import re
from lib import helpers
from lib import captcha_lib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

MAX_TRIES = 3

class ClickNUploadResolver(ResolveUrl):
    name = "clicknupload"
    domains = ['clicknupload.com', 'clicknupload.me', 'clicknupload.link', 'clicknupload.org']
    pattern = '(?://|\.)(clicknupload\.(?:com|me|link|org))/(?:f/)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': web_url
        }
        html = self.net.http_GET(web_url, headers=headers).content
        tries = 0
        while tries < MAX_TRIES:
            data = helpers.get_hidden(html)
            data.update(captcha_lib.do_captcha(html))
            html = self.net.http_POST(web_url, data, headers=headers).content
            r = re.search('''class="downloadbtn"[^>]+onClick\s*=\s*\"window\.open\('([^']+)''', html)
            if r:
                return r.group(1) + helpers.append_headers(headers)

            if tries > 0:
                common.kodi.sleep(1000)
                
            tries = tries + 1

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return 'https://clicknupload.org/%s' % media_id

    @classmethod
    def isPopup(self):
        return True
