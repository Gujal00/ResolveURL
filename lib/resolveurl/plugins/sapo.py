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
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class SapoResolver(ResolveUrl):
    name = "sapo"
    domains = ["videos.sapo.pt"]
    pattern = '(?://|\.)(videos\.sapo\.pt)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        if html:
            try:
                video_link = re.search(r'data-video-link=[\"\'](.+?)[\"\']', html).groups()[0]
                if video_link.startswith('//'): video_link = 'http:%s' % video_link
                return video_link
            except:
                raise ResolverError('No playable video found.')

        else:
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://%s/%s' % (host, media_id)
        
