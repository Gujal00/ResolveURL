"""
    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError

class MersalaResolver(ResolveUrl):
    name = "mersalaayitten.com"
    domains = ["mersalaayitten.com", "mersalaayitten.co", "mersalaayitten.us"]
    pattern = '(?://|\.)(mersalaayitten\.(?:com|co|us))/embed/([0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        headers = dict(resp._response.info().items())
        headers = {'Cookie': headers['set-cookie']}
        headers['User-Agent'] = common.FF_USER_AGENT
        r = re.search('config=(.*?)"', html)

        if r:
            stream_xml = r.group(1)
            headers['Referer'] = 'http://mersalaayitten.us/media/nuevo/player.swf?config=%s' % stream_xml
            response = self.net.http_GET(stream_xml, headers=headers)
            xmlhtml = response.content

            r2 = re.search('<file>(.*?)</file>', xmlhtml)

            stream_url = r2.group(1) + helpers.append_headers(headers)
        else:
            raise ResolverError('no file located')

        return stream_url

    def get_url(self, host, media_id):
        return 'http://mersalaayitten.us/embed/%s' % media_id
