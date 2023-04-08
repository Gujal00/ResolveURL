"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import random
import base64
import json
from resolveurl.lib import pyaes
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidCloud9Resolver(ResolveUrl):
    name = 'VidCloud9'
    domains = ['vidcloud9.com', 'vidnode.net', 'vidnext.net', 'vidembed.net', 'vidembed.cc', 'vidembed.io',
               'vidembed.me', 'membed.net', 'membed1.com', 'membed.co', 'movembed.cc']
    pattern = r'(?://|\.)((?:vidcloud9|vidnode|vidnext|(?:vid|m|mov)embed\d{0,1})\.(?:com?|net|cc|io|me))/' \
              r'(?:streaming|embedplus|load(?:server)?)(?:\.php)?\?id=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url}

        key = '25742532592138496744665879883281'.encode('utf8')
        iv = '9225679083961858'.encode('utf8')
        encryptor = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, iv))
        eid = encryptor.feed(media_id)
        eid += encryptor.feed()
        url = 'https://movembed.cc' + '/encrypt-ajax.php?id=' + base64.b64encode(eid).decode('utf8') \
            + '&c=aaaaaaaa&refer=none&alias={0}'.format(media_id)
        headers.update({'X-Requested-With': 'XMLHttpRequest'})
        js_data = json.loads(self.net.http_GET(url, headers=headers).content).get('data', None)
        if js_data:
            ct = base64.b64decode(js_data)
            decryptor = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
            ddata = decryptor.feed(ct)
            ddata += decryptor.feed()
            sources = json.loads(ddata.decode('utf-8').replace('\\', '')).get('source')
            if sources:
                sources = [(source.get('label').replace(' ', ''), source.get('file')) for source in sources if source.get('label') != 'Auto']
                headers.pop('X-Requested-With')
                source = helpers.pick_source(helpers.sort_sources_list(sources))
                return source + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://movembed.cc/loadserver.php?id={media_id}')

    def f_random(self, x):
        stime = ''
        for _ in range(x):
            stime += str(random.randint(0, 9))
        return stime
