"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class RuTubeResolver(ResolveUrl):
    name = "rutube.ru"
    domains = ['rutube.ru']
    pattern = '(?://|\.)(rutube\.ru)/(?:play/embed/|video/)([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        headers = {
            'User-Agent': common.ANDROID_USER_AGENT
        }

        json_url = 'http://rutube.ru/api/play/options/%s/?format=json&no_404=true' % media_id

        json_data = self.net.http_GET(json_url, headers=headers).content
        json_data = json.loads(json_data)['video_balancer']
        url = json_data.get('m3u8')
        if url is not None: return url

        json_url = json_data.get('json')
        json_data = self.net.http_GET(json_url, headers=headers).content
        try: return json.loads(json_data)['results'][0]
        except: pass

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://rutube.ru/play/embed/%s' % media_id
