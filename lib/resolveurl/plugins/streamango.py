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
import json
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError


logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

API_BASE_URL = 'https://api.fruithosted.net'
INFO_URL = API_BASE_URL + '/streaming/info'
GET_URL = API_BASE_URL + '/streaming/get?file={media_id}'
FILE_URL = API_BASE_URL + '/file/info?file={media_id}'

class StreamangoResolver(ResolveUrl):
    name = "streamango"
    domains = ['streamango.com', 'streamcherry.com', 'fruitstreams.com', 'fruitadblock.net', 'fruithosted.net', 'fruithosts.net']
    pattern = '(?://|\.)((?:stream(?:ango|cherry)|(?:fruit(?:streams|adblock|hosts)))\.(?:com|net))/(?:v/d|f|embed)/([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.RAND_UA}
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=self.headers).content
        
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
                    self.headers.update({'Referer': web_url})
                    return source + helpers.append_headers(self.headers)
        
        try:
            if not self.__file_exists(media_id):
                raise ResolverError('File Not Available')

            video_url = self.__check_auth(media_id)
            if not video_url:
                video_url = self.__auth_ip(media_id)
        except ResolverError:
            raise

        if video_url:
            return video_url + helpers.append_headers(self.headers)
        else:
            raise ResolverError(i18n('no_ip_authorization'))

    def __file_exists(self, media_id):
        js_data = self.__get_json(FILE_URL.format(media_id=media_id))
        return js_data.get('result', {}).get(media_id, {}).get('status') == 200

    def __auth_ip(self, media_id):
        js_data = self.__get_json(INFO_URL)
        pair_url = js_data.get('result', {}).get('auth_url', '')
        if pair_url:
            pair_url = pair_url.replace('\/', '/')
            header = i18n('stream_auth_header')
            line1 = i18n('auth_required')
            line2 = i18n('visit_link')
            line3 = i18n('click_pair').decode('utf-8') % pair_url
            with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
                return cd.start(self.__check_auth, [media_id])

    def __check_auth(self, media_id):
        try:
            js_data = self.__get_json(GET_URL.format(media_id=media_id))
        except ResolverError as e:
            status, msg = e
            if status == 403:
                return
            else:
                raise ResolverError(msg)

        return js_data.get('result', {}).get('url')

    def __get_json(self, url):
        result = self.net.http_GET(url, headers=self.headers).content
        common.logger.log(result)
        js_result = json.loads(result)
        if js_result['status'] != 200:
            raise ResolverError(js_result['status'], js_result['msg'])
        return js_result

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
        return self._default_get_url(host, media_id, 'https://{host}/embed/{media_id}')

    @classmethod
    def isPopup(self):
        return True
