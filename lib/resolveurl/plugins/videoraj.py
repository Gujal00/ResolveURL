"""
    resolveurl Kodi Addon
    Copyright (C) 2016 Gujal

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

# import re
# import urllib
# from resolveurl import common
# from resolveurl.resolver import ResolveUrl, ResolverError
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VideoRajResolver(ResolveUrl):
    name = 'videoraj.to'
    domains = ['videoraj.ec', 'videoraj.eu', 'videoraj.sx', 'videoraj.ch', 'videoraj.com', 'videoraj.to', 'videoraj.co']
    pattern = '(?://|\.)(videoraj\.(?:ec|eu|sx|ch|com|co|to))/(?:v(?:ideo)*/|embed\.php\?id=)([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content

        if 'vidError' in html:
            raise ResolverError('File Not Found or removed')

        sources = helpers.scrape_sources(html)
        return helpers.pick_source(sources)

    def get_url(self, host, media_id):
        return 'http://www.videoraj.to/embed.php?id=%s&playerPage=1&autoplay=1' % media_id
