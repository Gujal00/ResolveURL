"""
    resolveurl Kodi Addon

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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class StreamangoResolver(ResolveUrl):
    name = "streamango"
    domains = ['streamango.com', "streamcherry.com", "fruitstreams.com"]
    pattern = '(?://|\.)((?:stream(?:ango|cherry)|fruitstreams)\.com)/(?:v/d|f|embed)/([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            encoded = re.search('''srces\.push\(\s*{type:"video/mp4",src:\w+\('([^']+)',(\d+)''', html)
            if encoded:
                source = self.decode(encoded.group(1), int(encoded.group(2)))
                if source:
                    source = "http:%s" % source if source.startswith("//") else source
                    source = source.split("/")
                    if not source[-1].isdigit():
                      source[-1] = re.sub('[^\d]', '', source[-1])
                    source = "/".join(source)
                    headers.update({'Referer': web_url})
                    return source + helpers.append_headers(headers)
        
        raise ResolverError("Unable to locate video")
        
    def decode(self, encoded, code):
        _0x59b81a = ""
        k = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
        k = k[::-1]

        count = 0

        for index in range(0, len(encoded) - 1):
            while count <= len(encoded) - 1:
                _0x4a2f3a = k.index(encoded[count])
                count += 1
                _0x29d5bf = k.index(encoded[count])
                count += 1
                _0x3b6833 = k.index(encoded[count])
                count += 1
                _0x426d70 = k.index(encoded[count])
                count += 1

                _0x2e4782 = ((_0x4a2f3a << 2) | (_0x29d5bf >> 4))
                _0x2c0540 = (((_0x29d5bf & 15) << 4) | (_0x3b6833 >> 2))
                _0x5a46ef = ((_0x3b6833 & 3) << 6) | _0x426d70
                _0x2e4782 = _0x2e4782 ^ code

                _0x59b81a = str(_0x59b81a) + chr(_0x2e4782)

                if _0x3b6833 != 64:
                    _0x59b81a = str(_0x59b81a) + chr(_0x2c0540)
                if _0x3b6833 != 64:
                    _0x59b81a = str(_0x59b81a) + chr(_0x5a46ef)

        return _0x59b81a

    def get_url(self, host, media_id):
        if host.lower() == 'streamango.com':
            host = 'fruitstreams.com'
        return self._default_get_url(host, media_id, 'http://{host}/embed/{media_id}')
