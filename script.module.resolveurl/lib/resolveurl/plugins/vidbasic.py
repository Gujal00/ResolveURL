"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidBasicResolver(ResolveUrl):
    name = 'VidBasic'
    domains = ['vidbasic.top']
    pattern = r'(?://|\.)(vidbasic\.top)/(?:embed)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.RAND_UA}
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'''data-video="([^"]+)">Standard''', html)
        if r:
            headers.update({
                'Referer': 'https://{0}/'.format(host),
                'Origin': 'https://{0}'.format(host)
            })
            url2 = urllib_parse.urljoin(web_url, r.group(1))
            html2 = self.net.http_GET(url2, headers=headers).content
            r = re.search(r'data-name="crypto"\s*data-value="([^"]+)"', html2)
            if r:
                murl = self.vb_decrypt(r.group(1))
                if murl.startswith('http'):
                    return murl + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')

    @staticmethod
    def vb_decrypt(data):
        import six
        from resolveurl.lib import pyaes
        data = helpers.b64decode(data, binary=True)
        key = six.b('94588293375053432799222445521289')
        iv = six.b('5259228356829423')
        decryptor = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
        ddata = decryptor.feed(data)
        ddata += decryptor.feed()
        return ddata.decode('utf-8')
