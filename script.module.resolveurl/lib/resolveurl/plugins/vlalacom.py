"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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

from resolveurl.lib import helpers
from resolveurl.lib.jscrypto import jscrypto
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class VlalaComResolver(ResolveUrl):
    name = 'VlalaCom'
    domains = ['videoslala.com']
    pattern = r'(?://|\.)(videoslala\.com)/(?:v|e)/([^\n]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False

        web_url = self.get_url(host, media_id)
        if not referer:
            referer = urllib_parse.urljoin(web_url, '/')

        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}

        html = self.net.http_GET(web_url, headers=headers).content
        if 'Please Wait' in html:
            raise ResolverError('Please Wait Video Uploading.')

        r = re.search(r"_decx\('([^']+)", html)
        if r:
            data = json.loads(r.group(1))
            ct = data.get('ct', False)
            salt = codecs.decode(data.get('s'), 'hex')
            html2 = jscrypto.decode(ct, 'GDPlayer-JASm(8234_)9312HJASi23lakka', salt)
            html2 = html2[1:-1].replace('\\"', '"')
            s = re.search(r'{\s*url:\s*"([^"]+)', html2)
            if s:
                headers.update({'Referer': 'https://{}/'.format(host)})
                aurl = s.group(1).replace('\\', '')
                jd = json.loads(self.net.http_GET(aurl, headers=headers).content)
                url = jd.get('sources')[0].get('file')
                headers.update({'verifypeer': 'false'})
                return url + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
