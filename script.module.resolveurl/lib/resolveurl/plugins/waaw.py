"""
    Plugin for ResolveURL
    Copyright (C) 2023 MrDini123, gujal

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

import codecs
import json
import re

from base64 import b64decode
from random import choice
from six.moves import urllib_parse
from resolveurl.lib import helpers, captcha_window
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class WaawResolver(ResolveUrl):
    name = 'Waaw'
    domains = ['waaw.ac', 'netu.ac', 'hqq.ac', 'waaw.tv', 'netu.tv', 'hqq.to',
               'doplay.store', 'younetu.com']
    pattern = r'(?://|\.)((?:you)?(?:waaw|netu|hqq|doplay)\.(?:ac|tv|to|store|com))/' \
              r'(?:watch_video\.php\?v=|.+?\?vid=|e/|f/)([a-zA-Z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r"'videoid':\s*'([^']+)", html)
        if r:
            video_id = r.group(1)
            video_key = re.search(r"'videokey':\s*'([^']+)", html).group(1)
            adbn = re.search(r"adbn\s*=\s*'([^']+)", html).group(1)
            data = {"videoid": video_id, "videokey": video_key, "width": 400, "height": 400}
            headers.update({
                'Referer': web_url,
                'Origin': urllib_parse.urljoin(web_url, '/')[:-1],
                'X-Requested-With': 'XMLHttpRequest'
            })
            imgurl = urllib_parse.urljoin(web_url, '/player/get_player_image.php')
            html2 = self.net.http_POST(imgurl, form_data=data, headers=headers, jdata=True).content
            if 'Video not found' in html2:
                raise ResolverError('Video Not Found')
            json_data = json.loads(html2)

            if json_data.get('try_again') == '1':
                raise ResolverError('Too many attempts. Please try again later.')

            hash_img = json_data['hash_image']
            image = json_data['image'].replace('data:image/jpeg;base64,', '')
            image = b64decode(image + "==")
            window = captcha_window.CaptchaWindow(image, 400, 400)
            window.doModal()

            if not window.finished:
                return

            x = window.solution_x
            y = window.solution_y

            data = {
                'adb': adbn,
                'sh': self.random_sha1(),
                'ver': '4',
                'secure': '0',
                'htoken': '',
                'v': media_id,
                'token': '',
                'gt': '',
                'embed_from': '0',
                'wasmcheck': 1,
                'adscore': '',
                'click_hash': urllib_parse.quote(hash_img),
                'clickx': x,
                'clicky': y,
            }
            md5url = urllib_parse.urljoin(web_url, '/player/get_md5.php')
            html3 = self.net.http_POST(md5url, form_data=data, headers=headers, jdata=True).content
            json_data = json.loads(html3)

            if json_data.get("try_again") == "1":
                raise ResolverError('Wrong captcha. Please try again.')

            decrypted_link = self.un(json_data['obf_link'])
            if decrypted_link:
                strurl = "https:{0}.mp4.m3u8".format(decrypted_link)
                headers.pop('X-Requested-With')
                return strurl + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')

    @staticmethod
    def un(strid):
        strid = strid[1:]
        j = 0
        s2 = ''
        while j < len(strid):
            s2 += '\\u0' + strid[j:(j + 3)]
            j += 3
        s2 = codecs.decode(s2, encoding='unicode-escape') if common.kodi_version > 18.9 else s2.decode('raw_unicode_escape')
        return s2

    @staticmethod
    def random_sha1():
        return ''.join([choice('0123456789abcdef') for x in range(40)])

    @classmethod
    def isPopup(self):
        return True
