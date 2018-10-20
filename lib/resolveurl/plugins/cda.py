"""
    resolveurl XBMC Addon
    Copyright (C) 2015 tknorris

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
from lib import jsunpack
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import string

rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")

class CdaResolver(ResolveUrl):
    name = "cda"
    domains = ['cda.pl', 'www.cda.pl', 'ebd.cda.pl']
    pattern = '(?://|\.)(cda\.pl)/(?:.\d+x\d+|video)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.CHROME_USER_AGENT}
		
        player_headers = {'Cookie': 'PHPSESSID=1', 'Referer': web_url, 'User-Agent': common.CHROME_USER_AGENT}
        player_headers.update(headers)

        html = self.net.http_GET(web_url, headers=headers).content
        try: html = html.encode('utf-8')
        except: pass
        match = re.findall('data-quality="(.*?)" href="(.*?)".*?>(.*?)</a>', html, re.DOTALL)
        if match:
            mylinks = sorted(match, key=lambda x: x[2])
            html = self.net.http_GET(mylinks[-1][1], headers=headers).content
            
        from HTMLParser import HTMLParser
        match = re.search('''['"]file['"]:\s*['"](.+?)['"]''', HTMLParser().unescape(html))
        if match:
            mylink = match.group(1).replace("\\", "")
            return self.__check_vid(mylink) + helpers.append_headers(player_headers)

        html = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
        match = re.search('src="(.*?\.mp4)"', html)
        if match:
            return self.__check_vid(match.group(1)) + helpers.append_headers(player_headers)

        raise ResolverError('Video Link Not Found')

    def __check_vid(self, video_link):
        if re.match('uggc', video_link):
            video_link = string.translate(video_link, rot13)
            video_link = video_link[:-7] + video_link[-4:]
        return video_link

    def get_url(self, host, media_id):
        return 'http://ebd.cda.pl/647x500/%s' % media_id
