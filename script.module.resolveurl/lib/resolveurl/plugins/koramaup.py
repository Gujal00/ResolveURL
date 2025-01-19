"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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

import binascii
import re
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from six.moves import urllib_parse


class KoramaUpResolver(ResolveUrl):
    name = 'KoramaUp'
    domains = ['koramaup.com']
    pattern = r'(?://|\.)(koramaup\.com)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url}
        resp = self.net.http_GET(web_url, headers)
        r = re.search(r',\s*f\("([^"]+)', resp.content)
        if r:
            uri = self.get_uri(r.group(1))
            cookie = resp.get_headers(as_dict=True).get('Set-Cookie', '')
            headers.update({'Cookie': cookie.split(';')[0] + '; cookieconsent=1'})
            common.kodi.sleep(5000)
            url = helpers.get_redirect_url(uri, headers=headers)
            if url != uri:
                headers.pop('Cookie')
                return urllib_parse.quote(url, '/:=&?') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @staticmethod
    def get_uri(ct):
        ch = binascii.unhexlify(ct)
        surl = ''
        for i in range(len(ch)):
            surl += chr((ch[i] if isinstance(ch[i], int) else ord(ch[i])) ^ 122)
        return surl
