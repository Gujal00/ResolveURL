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
from resolveurl.lib.pyaes import util as pyaes_util


class StreamUpResolver(ResolveUrl):
    name = 'StreamUp'
    domains = ['streamup.ws', 'strmup.to']
    pattern = r'(?://|\.)(stre?a?mup\.(?:ws|to))/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        try:
            user_agent = common.RAND_UA
            headers = {"User-Agent": user_agent, "Referer": 'https://{0}/'.format(host)}

            content = self.net.http_GET(web_url, headers=headers).content

            session_id_match = re.search(r"['\"]([a-f0-9]{32})['\"]", content)
            encrypted_data_match = re.search(r"data-value=['\"]([A-Za-z0-9+/=]{200,})['\"]", content)

            if not encrypted_data_match or not session_id_match:
                raise ResolverError("Could not find 'encrypted data' or 'session id' on the page.")

            session_id = session_id_match.group(1)
            encrypted_data_b64 = encrypted_data_match.group(1)

            parsed_url = urllib_parse.urlparse(web_url)
            base_url_with_scheme = "{0}://{1}".format(parsed_url.scheme, parsed_url.netloc)
            key_url = "{0}/ajax/stream?session={1}".format(base_url_with_scheme, session_id)

            key_headers = {"User-Agent": user_agent, "Referer": web_url}

            key_b64 = self.net.http_GET(key_url, headers=key_headers).content
            key = helpers.b64decode(key_b64, binary=True)

            encrypted_data = helpers.b64decode(encrypted_data_b64, binary=True)
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]

            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
            decrypted_padded = decrypter.feed(ciphertext)
            decrypted_padded += decrypter.feed()

            decrypted_data = pyaes_util.strip_PKCS7_padding(decrypted_padded)
            decrypted_data_str = six.ensure_str(decrypted_data)

            stream_info = json.loads(decrypted_data_str)
            stream_url = stream_info.get("streaming_url")

            playback_headers = {
                "User-Agent": user_agent,
                "Referer": base_url_with_scheme + "/",
                "Origin": base_url_with_scheme
            }

            return stream_url + helpers.append_headers(playback_headers)


        except Exception as e:
            common.logger.log('StreamUp Error: %s' % e, common.log_utils.LOGWARNING)
            raise ResolverError('An unexpected error occurred with the StreamUp resolver: %s' % e)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
