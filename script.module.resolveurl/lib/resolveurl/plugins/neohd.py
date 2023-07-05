"""
    Plugin for ResolveURL
    Copyright (C) 2022 gujal

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
import json
import codecs
import time
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.lib.jscrypto import jscrypto
from resolveurl.resolver import ResolveUrl, ResolverError


class NeoHDResolver(ResolveUrl):
    name = 'NeoHD'
    domains = ['neohd.xyz', 'ninjahd.one']
    pattern = r'(?://|\.)((?:neo|ninja)hd\.(?:xyz|one))/embed/([0-9a-zA-Z-]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r"playerConfig\s*=\s*({.+?})", html)
        if r:
            data = json.loads(r.group(1))
            ct = data.get('ct', False)
            salt = codecs.decode(data.get('s'), 'hex')
            html2 = jscrypto.decode(ct, 'F1r3b4Ll_GDP~5H', salt)
            html2 = html2[1:-1].replace('\\"', '"')
            s = re.search(r'apiQuery":"([^"]+)', html2)
            if s:
                headers.update({'Referer': web_url, 'X-Requested-With': 'XMLHttpRequest'})
                aurl = 'https://{0}/api/?{1}&_={2}'.format(host, s.group(1), int(time.time() * 1000))
                jd = json.loads(self.net.http_GET(aurl, headers=headers).content)
                url = jd.get('sources')[0].get('file').replace(' ', '%20')
                if url.startswith('//'):
                    url = 'https:' + url
                headers.pop('X-Requested-With')
                return url + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
