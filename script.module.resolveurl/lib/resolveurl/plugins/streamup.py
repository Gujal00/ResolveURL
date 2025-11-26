"""
    Plugin for ResolveURL
    Copyright (c) 2025 gujal

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
import json
import six
from six.moves import urllib_parse

from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError

from resolveurl.lib import pyaes


class StreamUpResolver(ResolveUrl):
    name = 'StreamUp'
    domains = ['streamup.ws', 'streamup.cc', 'strmup.to', 'strmup.cc', 'vfaststream.com']
    pattern = r'(?://|\.)((?:vfast)?stre?a?m(?:up)?\.(?:ws|cc|to|com))/(?:v/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        user_agent = common.RAND_UA
        ref = urllib_parse.urljoin(web_url, '/')
        stream_url = ''
        headers = {"User-Agent": user_agent, "Referer": ref}
        content = self.net.http_GET(web_url, headers=headers).content

        session_id_match = re.search(r"'([a-f0-9]{32})'", content)
        encrypted_data_match = re.search(r"'([A-Za-z0-9+/=]{200,})'", content)

        if encrypted_data_match and session_id_match:
            session_id = session_id_match.group(1)
            encrypted_data_b64 = encrypted_data_match.group(1)
            key_url = "{0}/ajax/stream?session={1}".format(ref[:-1], session_id)
            key_b64 = self.net.http_GET(key_url, headers=headers).content
            key = helpers.b64decode(key_b64, binary=True)
            encrypted_data = helpers.b64decode(encrypted_data_b64, binary=True)
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]

            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
            decrypted_data = decrypter.feed(ciphertext)
            decrypted_data += decrypter.feed()

            stream_info = json.loads(six.ensure_str(decrypted_data))
            stream_url = stream_info.get("streaming_url")
        else:
            surl = '{0}/ajax/stream?filecode={1}'.format(ref[:-1], media_id)
            sdata = self.net.http_GET(surl, headers=headers).content
            stream_info = json.loads(sdata)
            stream_url = stream_info.get("streaming_url")

        if stream_url:
            headers.update({"Origin": ref[:-1]})
            stream_url = stream_url.replace('\r', '').replace('\n', '')
            return stream_url + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
