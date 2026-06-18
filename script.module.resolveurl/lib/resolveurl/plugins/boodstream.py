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

import time
import uuid
from six.moves import urllib_parse
from resolveurl.lib import helpers, pyaes
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class BoodStreamResolver(ResolveUrl):
    name = 'BoodStream'
    domains = [
        'boodstream.cc', 'boodstream.club', 'boodstream.cam',
        'glunvropix.space', 'flowveins.online', 'bleedtube.site'
    ]
    pattern = (
        r'(?://|\.)((?:boodstream|glunvropix|flowveins|bleedtube)'
        r'\.(?:cc|club|cam|space|online|site))/([0-9a-zA-Z]+)'
    )

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        a_req_id = str(uuid.uuid4())
        a_sign = self.get_asign(a_req_id)
        userStr = str(uuid.uuid4())
        headers = {
            'Referer': ref,
            'Origin': ref[:-1],
            'User-Agent': common.RAND_UA,
            'a-req-id': a_req_id,
            'a-sign': a_sign,
            'a-time': str(int(time.time() * 1000)),
            'country-no': 'en-US'
        }
        params = {
            'videoId': media_id,
            'userStr': userStr
        }
        api_url = 'https://apbood.boodstream.com/v1/file/getVideo?{0}'.format(urllib_parse.urlencode(params))
        r = self.net.http_GET(api_url, headers=headers).json.get('data')
        if r:
            src = r.get('videoUrl')
            if src:
                headers = {'User-Agent': common.RAND_UA}
                return src + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://share.{host}/{media_id}')

    @staticmethod
    def get_asign(payload):
        KEY = "kP9rT2vN8mJ1bZ6c".encode('utf-8')
        IV = "d7e8f9a0b1c2d3e4".encode('utf-8')
        plaintext = "t:WF;kZKMcXwKqE" + payload
        encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(KEY, IV))
        encrypted = encrypter.feed(plaintext)
        encrypted += encrypter.feed()
        return helpers.b64encode(encrypted)
