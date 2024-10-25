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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class TurboVidResolver(ResolveUrl):
    name = 'TurboVid'
    domains = ['turbovid.eu']
    pattern = r'(?://|\.)(turbovid\.eu)/embed/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': ref}
        resp = self.net.http_GET(web_url, headers).content
        r = re.search(r'''const\s*apkey\s*=\s*"([^"]+).+?const\s*xxid\s*=\s*"([^"]+)''', resp, re.DOTALL)
        if r:
            jurl = 'https://{0}/api/cucked/juice_key'.format(host)
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            jresp = self.net.http_GET(jurl, headers).content
            j = re.search(r'''juice":"([^"]+)''', jresp)
            if j:
                jsurl = 'https://{0}/api/cucked/the_juice/?{1}={2}'.format(host, r.group(1), r.group(2))
                jsresp = self.net.http_GET(jsurl, headers).content
                js = re.search(r'''data":"([^"]+)''', jsresp)
                if js:
                    uri = self.get_uri(js.group(1), j.group(1))
                    headers.pop('X-Requested-With')
                    headers.update({'Origin': ref[:-1]})
                    return uri + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')

    @staticmethod
    def get_uri(ct, key):
        ch = binascii.unhexlify(ct)
        surl = ''
        for i in range(len(ch)):
            surl += chr((ch[i] if isinstance(ch[i], int) else ord(ch[i])) ^ ord(key[i % len(key)]))
        return surl
