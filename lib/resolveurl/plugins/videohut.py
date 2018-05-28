"""
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

import re
import urllib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VideoHutResolver(ResolveUrl):
    name = "videohut.to"
    domains = ["videohut.to"]
    pattern = '(?://|\.)(videohut\.to)/(?:v\/|embed.php\?id=)([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        key = re.compile('key\s*:\s*[\'"](.+?)[\'"]').findall(html)
        if key:
            key = urllib.quote_plus(key[0]).replace('.', '%2E').replace('-', '%2D')

        filekey = re.compile('file\s*:\s*[\'"](.+?)[\'"]').findall(html)
        if filekey:
            filekey = urllib.quote_plus(filekey[0]).replace('.', '%2E').replace('-', '%2D')

        for _i in range(0, 3):
            try:
                player_url = 'http://www.videohut.to/api/player.api.php?key=%s&file=%s' % (key, filekey)
                html = self.net.http_GET(player_url).content

                stream_url = re.search('url=(.+?)&', html).group(1)
                stream_url = urllib.unquote(stream_url)

                return stream_url
            except:
                pass

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://www.videohut.to/embed.php?id=%s' % media_id
