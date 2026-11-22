"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal

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

import json
import re
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VidHlsResolver(ResolveUrl):
    name = 'VidHls'
    domains = ['vidhls.com']
    pattern = r'(?://|\.)(vidhls\.com)/player/index.php\?data=([0-9a-zA-Z:/$.]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        if not referer:
            referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': referer}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'FirePlayer\([^{]+(.*?),\s*(?:false|true)', html)
        if r:
            v = json.loads(r.group(1))
            str_url = 'https://' + host + v.get('videoUrl') + '?s=' + v.get('videoServer')
            headers.update({'Referer': urllib_parse.urljoin(web_url, '/')})
            return str_url + helpers.append_headers(headers)

        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}')
