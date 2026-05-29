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

from resolveurl.lib import helpers
import ast
import re
import json
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class GUploadResolver(ResolveUrl):
    name = 'GUpload'
    domains = ['gupload.xyz']
    pattern = r'(?://|\.)(gupload\.xyz)/data/e/([0-9a-f]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = ''
        if common.BP_ENABLED:
            bp_url = urllib_parse.urljoin(common.BP_URL, '/v1')
            data = {
                "cmd": "request.get",
                "url": web_url,
                "maxTimeout": common.BP_TIMEOUT * 1000
            }
            r = self.net.http_POST(bp_url, form_data=data, jdata=True, timeout=common.BP_TIMEOUT + 20).content
            r = json.loads(r)
            if r.get('message') == 'Success':
                r = r.get('solution')
                html = r.get('response')
        else:
            import cloudscraper
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
                delay=4
            )
            html = scraper.get(web_url, headers=headers, timeout=20).text

        key = re.search(r'''_p=(\[.*?])''', html)
        edata = re.findall(r'''_cfg\s*=\s*[^']+'([^']+)''', html)
        if key and edata:
            edata = edata[-1]
            key = ''.join(ast.literal_eval(key.group(1)))
            resp = self.__gdecrypt(edata, key)
            if resp:
                strurl = resp.get('videoUrl')
                if strurl:
                    return strurl + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/data/e/{media_id}')

    @staticmethod
    def __gdecrypt(cfg, k):
        parts = cfg.split('~')
        if len(parts) < 2:
            return None
        b = helpers.b64decode(parts[1])
        r = ''
        for i in range(len(b)):
            r += chr(ord(b[i]) ^ ord(k[i % len(k)]))
        try:
            r = json.loads(r)
        except json.JSONDecodeError:
            return None
        return r
