"""
    Plugin for ResolveURL
    Copyright (C) 2024 Ghb3245

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
import re
import time
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from six.moves import urllib_parse


class TeraBoxResolver(ResolveUrl):
    name = 'Terabox'
    domains = ['terabox.com', 'terabox.app']
    pattern = r'(?://|\.)(terabox\.(?:com|app))/sharing/(?:embed|link)\?surl=([0-9a-zA-Z-_]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content

        r = re.search(r'''"jsToken":"function%20fn%28a%29%7Bwindow.jsToken%20%3D%20a%7D%3Bfn%28%22([^"]+)%22%29''', html, re.DOTALL)
        if r:
            jsToken = r.group(1)
            app_id = '250528'
            teralink = 'https://www.{0}/api/shorturlinfo?app_id={1}&web=1&channel=dubox&clienttype=0&jsToken={2}&shorturl=1{3}&root=1&scene='.format(host, app_id, jsToken, media_id)
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                "referer": web_url,
            })
            resp = json.loads(self.net.http_GET(teralink, headers=headers).content)
            m3u8 = 'https://www.{0}/share/extstreaming.m3u8'.format(host)
            timestamp = int(time.time() * 1000)
            params = {
                'app_id': app_id,
                'channel': 'dubox',
                'clienttype': 0,
                'uk': resp["uk"],
                'shareid': resp["shareid"],
                'type': 'M3U8_AUTO_1080',
                'fid': resp["list"][0]["fs_id"],
                'sign': resp["sign"],
                'timestamp': timestamp,
            }
            m3u8 = 'https://www.{0}/share/extstreaming.m3u8?{1}'.format(host, urllib_parse.urlencode(params))
            return m3u8

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/sharing/embed?surl={media_id}')
