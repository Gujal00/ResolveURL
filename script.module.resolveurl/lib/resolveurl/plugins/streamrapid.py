"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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
from resolveurl.lib.pyaes import openssl_aes
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamRapidResolver(ResolveUrl):
    name = 'StreamRapid'
    domains = ['streamrapid.ru', 'rabbitstream.net', 'mzzcloud.life', 'dokicloud.one']
    pattern = r'(?://|\.)((?:rabbitstream|streamrapid|(?:mzz|doki)cloud)\.(?:ru|net|life|one))/embed-([^\n$]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}

        html = self.net.http_GET(web_url, headers).content
        surl = re.findall(r'<script\s*type.+?src="([^"]+)', html)
        if surl:
            surl = urllib_parse.urljoin(referer, surl[0])
            tries = 0
            key = ''
            while tries < 3 and not key:
                js = self.net.http_GET(surl, headers).content
                r = re.search(r"const\s*_0x[0-9a-f]{1,6}='([^']+)", js)
                if r:
                    key = r.group(1)
                else:
                    common.kodi.sleep(5000)
                    tries += 1

            if key:
                headers.update({'X-Requested-With': 'XMLHttpRequest'})
                mid = media_id.split('?')[0]
                mid = mid.replace('/', '/getSources?id=')
                aurl = 'https://{0}/ajax/embed-{1}'.format(host, mid)
                ahtml = self.net.http_GET(aurl, headers).content
                sources = json.loads(ahtml).get('sources')
                if sources:
                    OpenSSL_AES = openssl_aes.AESCipher()
                    sources = json.loads(OpenSSL_AES.decrypt(sources, key))
                    source = sources[0]
                    if source:
                        headers.pop('X-Requested-With')
                        return source.get('file') + helpers.append_headers(headers)
                raise ResolverError('File Not Found or removed')
            raise ResolverError('Unable to locate Decryption key')
        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}')
