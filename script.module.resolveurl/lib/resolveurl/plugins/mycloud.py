"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de, gujal

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

from resolveurl.plugins.__resolve_generic__ import ResolveGeneric


class MyCloudResolver(ResolveGeneric):
    name = 'MyCloud'
    domains = ['mycloud.to', 'mcloud.to', 'vizcloud.digital', 'vizcloud.cloud']
    pattern = r'(?://|\.)((?:my?|viz)cloud\.(?:to|digital|cloud))/(?:embed|e)/([0-9a-zA-Z]+)'

    def get_url(self, host, media_id):
        media_id = self.__mc_encode(media_id)
        return self._default_get_url(host, media_id, template='https://{host}/mediainfo/{media_id}?key=Q1nbJDsdM2BpgXNU')

    def __mc_encode(self, media_id):
        import six
        import base64

        def encode2x(mstr):
            # Thanks to https://github.com/mbebe for the encode2x function
            STANDARD_ALPHABET = six.ensure_binary('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
            CUSTOM_ALPHABET = six.ensure_binary('51wJ0FDq/UVCefLopEcmK3ni4WIQztMjZdSYOsbHr9R2h7PvxBGAuglaN8+kXT6y')
            if six.PY2:
                import string
                ENCODE_TRANSx = string.maketrans(STANDARD_ALPHABET, CUSTOM_ALPHABET)
            else:
                ENCODE_TRANSx = bytes.maketrans(STANDARD_ALPHABET, CUSTOM_ALPHABET)
                mstr = mstr.encode('latin-1')
            return base64.b64encode(mstr).translate(ENCODE_TRANSx)

        media_id = encode2x(media_id)
        key = 'RTorhhm9RwQwUjOi'

        f_list = list(range(256))
        k = 0
        for i in range(256):
            k = (k + f_list[i] + ord(key[i % len(key)])) % 256
            tmp = f_list[i]
            f_list[i] = f_list[k]
            f_list[k] = tmp

        k = 0
        c = 0
        emid = ''
        for i in range(len(media_id)):
            c = (c + i) % 256
            k = (k + f_list[c % 256]) % 256
            tmp = f_list[c]
            f_list[c] = f_list[k]
            f_list[k] = tmp
            if six.PY2:
                emid += chr(ord(media_id[i]) ^ f_list[(f_list[c] + f_list[k]) % 256])
            else:
                emid += chr(ord(media_id[i]) if isinstance(media_id[i], six.string_types) else media_id[i] ^ f_list[(f_list[c] + f_list[k]) % 256])

        emid = six.ensure_str(encode2x(emid)).replace('/', '_').replace('=', '')

        return emid
