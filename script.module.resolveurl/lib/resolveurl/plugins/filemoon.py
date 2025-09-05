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
               'filemoon.wf', 'cinegrab.com', 'filemoon.eu', 'filemoon.art', 'moonmov.pro',
               'kerapoxy.cc', 'furher.in', '1azayf9w.xyz', '81u6xl9d.xyz', 'smdfs40r.skin',
               'bf0skv.org', 'z1ekv717.fun', 'l1afav.net', '222i8x.lol', '8mhlloqo.fun', '96ar.com',
               'xcoic.com', 'f51rm.com', 'c1z39.com', 'boosteradx.online']
    pattern = r'(?://|\.)((?:filemoon|cinegrab|moonmov|kerapoxy|furher|1azayf9w|81u6xl9d|' \
              r'smdfs40r|bf0skv|z1ekv717|l1afav|222i8x|8mhlloqo|96ar|xcoic|f51rm|c1z39|boosteradx)' \
              r'\.(?:sx|to|s?k?in|link|nl|wf|com|eu|art|pro|cc|xyz|org|fun|net|lol|online))' \
              r'/(?:e|d|download)/([0-9a-zA-Z$:/._-]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False

        if '/' in media_id:
            media_id = media_id.split('/')[0]

        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Cookie': '__ddg1_=PZYJSmASXDCQGP6auJU9; __ddg2_=hxAe1bBqtlYhVSik'}
        if referer:
            headers.update({'Referer': referer})

        html = self.net.http_GET(web_url, headers=headers).content
        if '<h1>Page not found</h1>' in html or '<h1>This video cannot be watched under this domain</h1>' in html:
            web_url = web_url.replace('/e/', '/d/')
            html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'<iframe\s*src="([^"]+)', html, re.DOTALL)
        if r:
            headers.update({'accept-language': 'en-US,en;q=0.9',
                            'sec-fetch-dest': 'iframe',
                            'Referer': web_url})
            web_url = r.group(1)
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
                headers.pop('Cookie')
                headers["verifypeer"] = "false"
                return surl + helpers.append_headers(headers)
        else:
            r = re.search(r'sources:\s*\[{\s*file:\s*"([^"]+)', html, re.DOTALL)
            if r:
                headers.pop('Cookie')
                headers.update({
                    'Referer': web_url,
                    'Origin': urllib_parse.urljoin(web_url, '/')[:-1],
                    "verifypeer": "false"
                })
                return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
