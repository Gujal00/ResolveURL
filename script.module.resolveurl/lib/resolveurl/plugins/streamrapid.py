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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.lib.pyaes import openssl_aes
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamRapidResolver(ResolveUrl):
    name = 'StreamRapid'
    domains = ['streamrapid.ru', 'rabbitstream.net', 'mzzcloud.life']
    pattern = r'(?://|\.)((?:rabbitstream|streamrapid|mzzcloud)\.(?:ru|net|life))/embed-([^\n]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://{0}/'.format(host),
                   'X-Requested-With': 'XMLHttpRequest'}
        html = self.net.http_GET(web_url, headers).content
        sources = json.loads(html).get('sources')
        if sources:
            OpenSSL_AES = openssl_aes.AESCipher()
            try:
                sources = json.loads(OpenSSL_AES.decrypt(sources, '69932eff70fd109a'))
                source = sources[0]
            except:
                raise ResolverError('Decrypt key changed')

            if source:
                headers.pop('X-Requested-With')
                return source.get('file') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        media_id = media_id.split('?')[0]
        media_id = media_id.replace('/', '/getSources?id=')
        return self._default_get_url(host, media_id, template='https://{host}/ajax/embed-{media_id}')
