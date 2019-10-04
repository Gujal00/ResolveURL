'''
Plugin for ResolveURL
Copyright (C) 2018 gujal
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

import re, urllib
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

def rot47(s):
    x = []
    for i in xrange(len(s)):
        j = ord(s[i])
        if j >= 33 and j <= 126:
            x.append(chr(33 + ((j + 14) % 94)))
        else:
            x.append(s[i])
    return ''.join(x)

class VivosxResolver(ResolveUrl):
    name = "vivosx"
    domains = ["vivo.sx"]
    pattern = '(?://|\.)(vivo\.sx)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content

        r = re.findall('InitializeStream.*?source:\s{0,1}[\'|\"](.*?)[\'|\"],', html, re.S)

        if r:
            return rot47(urllib.unquote(r[0])) + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return 'https://vivo.sx/%s' % media_id
