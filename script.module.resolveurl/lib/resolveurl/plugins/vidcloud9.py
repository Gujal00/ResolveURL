"""
Plugin for ResolveUrl
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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidCloud9Resolver(ResolveUrl):
    name = 'vidcloud9.com'
    domains = ['vidcloud9.com', 'vidnode.net', 'vidnext.net', 'vidembed.net', 'vidembed.cc', 'vidembed.io',
               'vidembed.me']
    pattern = r'(?://|\.)((?:vidcloud9|vidnode|vidnext|vidembed)\.(?:com|net|cc|io|me))/' \
              r'(?:streaming|embedplus|load(?:server)?)(?:\.php)?\?id=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://vidembed.me/'}

        key = '25746538592938496764662879833288'.encode('utf8')
        iv = self.f_random(16)
        encryptor = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, iv.encode('utf8')))
        eid = encryptor.feed(media_id)
        eid += encryptor.feed()
        url = 'https://vidembed.me' + '/encrypt-ajax.php?id=' + base64.b64encode(eid).decode('utf8') \
            + '&refer=none&time=' + self.f_random(2) + iv + self.f_random(2)
        headers.update({'X-Requested-With': 'XMLHttpRequest'})
        js_data = json.loads(self.net.http_GET(url, headers=headers).content)
        sources = js_data.get('source', None)
        if sources:
            sources = [(source.get('label'), source.get('file')) for source in sources]
            headers.pop('X-Requested-With')
            source = helpers.pick_source(helpers.sort_sources_list(sources))
            return source + helpers.append_headers(headers)

        # Try Beta Server if no sources found with earlier method
        headers.pop('X-Requested-With')
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.scrape_sources(html)
        if sources:
            headers.update({'Origin': 'https://vidembed.me'})
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidembed.me/loadserver.php?id={media_id}')

    def f_random(self, x):
        stime = ''
        for _ in range(x):
            stime += str(random.randint(0, 9))
        return stime
