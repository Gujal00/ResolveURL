"""
    Plugin for ResolveUrl
    Copyright (C) 2023 shellc0de, gujal

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class FileMoonResolver(ResolveUrl):
    name = 'FileMoon'
    domains = ['filemoon.sx', 'filemoon.to', 'filemoon.in', 'filemoon.link', 'filemoon.nl',
               'filemoon.wf', 'cinegrab.com', 'filemoon.eu', 'filemoon.art', 'moonmov.pro']
    pattern = r'(?://|\.)((?:filemoon|cinegrab|moonmov)\.(?:sx|to|in|link|nl|wf|com|eu|art|pro))' \
              r'/(?:e|d|download)/([0-9a-zA-Z$:/.]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False

        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        if referer:
            headers.update({'Referer': referer})

        html = self.net.http_GET(web_url, headers=headers).content
        html += helpers.get_packed_data(html)
        r = re.search(r'var\s*postData\s*=\s*(\{.+?\})', html, re.DOTALL)
        if r:
            r = r.group(1)
            pdata = {
                'b': re.findall(r"b:\s*'([^']+)", r)[0],
                'file_code': re.findall(r"file_code:\s*'([^']+)", r)[0],
                'hash': re.findall(r"hash:\s*'([^']+)", r)[0]
            }
            headers.update({
                'Referer': web_url,
                'Origin': urllib_parse.urljoin(web_url, '/')[:-1],
                'X-Requested-With': 'XMLHttpRequest'
            })
            edata = self.net.http_POST(urllib_parse.urljoin(web_url, '/dl'), pdata, headers=headers).content
            edata = json.loads(edata)[0]
            surl = helpers.tear_decode(edata.get('file'), edata.get('seed'))
            if surl:
                headers.pop('X-Requested-With')
                return surl + helpers.append_headers(headers)
        else:
            r = re.search(r'sources:\s*\[{\s*file:\s*"([^"]+)', html, re.DOTALL)
            if r:
                headers.update({
                    'Referer': web_url,
                    'Origin': urllib_parse.urljoin(web_url, '/')[:-1]
                })
                return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
