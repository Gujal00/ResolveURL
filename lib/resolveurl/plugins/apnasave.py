"""
    resolveurl Kodi plugin
    Copyright (C) 2016 Gujal

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

class ApnaSaveResolver(ResolveUrl):
    name = "apnasave.com"
    domains = ["apnasave.club"]
    pattern = '(?://|\.)(apnasave\.club)/embed/([0-9a-f]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        headers = dict(resp._response.info().items())
        headers = {'Cookie': headers['set-cookie']}
        headers['User-Agent'] = common.FF_USER_AGENT
        r = re.search('player.swf\?f=(.*?)"', html)

        if r:
            stream_xml = r.group(1)
            headers['Referer'] = 'http://www.apnasave.club/media/player/player.swf?f=%s' % stream_xml
            response = self.net.http_GET(stream_xml, headers=headers)
            xmlhtml = response.content

            r2 = re.search('<src>(.*?)</src>', xmlhtml)

            stream_url = r2.group(1) + helpers.append_headers(headers)
        else:
            raise ResolverError('no file located')

        return stream_url

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/embed/{media_id}')
