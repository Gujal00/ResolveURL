"""
    resolveurl XBMC Addon
    Copyright (C) 2011 anilkuj

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
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VeohResolver(ResolveUrl):
    name = "veoh"
    domains = ["veoh.com"]
    pattern = '(?://|\.)(veoh\.com)/(?:watch/|.+?permalinkId=)?([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        html = self.net.http_GET("http://www.veoh.com/iphone/views/watch.php?id=" + media_id + "&__async=true&__source=waBrowse").content
        if not re.search('This video is not available on mobile', html):
            r = re.compile("watchNow\('(.+?)'").findall(html)
            if (len(r) > 0):
                return r[0]

        url = 'http://www.veoh.com/rest/video/' + media_id + '/details'
        html = self.net.http_GET(url).content
        file_id = re.compile('fullPreviewHashPath="(.+?)"').findall(html)

        if len(file_id) == 0:
            raise ResolverError('File Not Found or removed')

        return file_id[0]

    def get_url(self, host, media_id):
        return 'http://veoh.com/watch/%s' % media_id
