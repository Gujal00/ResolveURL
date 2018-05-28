"""
    Kodi resolveurl plugin
    Copyright (C) 2016  tknorris

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
import urllib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class TudouResolver(ResolveUrl):
    name = 'Tudou'
    domains = ['tudou.com']
    pattern = '(?://|\.)(tudou\.com)/programs/view/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        swf = re.findall('(http.+?\.swf)', html)[0]
        sid = re.findall('areaCode\s*:\s*"(\d+)', html)[0]
        oid = re.findall('"k"\s*:\s*(\d+)', html)[0]

        f_url = 'http://v2.tudou.com/f?id=%s&sid=%s&hd=3&sj=1' % (oid, sid)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': swf}

        html = self.net.http_GET(f_url, headers=headers).content

        url = re.findall('>(http.+?)<', html)[0]
        url = url.replace('&amp;', '&')

        video = self.net.http_HEAD(url, headers=headers).get_headers()
        video = [i for i in video if 'video' in i]

        if not video:
            raise ResolverError('File not found')

        url += '|%s' % urllib.urlencode(headers)
        return url

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return 'http://www.tudou.com/programs/view/%s/' % media_id
