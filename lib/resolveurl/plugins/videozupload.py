"""
    resolveurl Kodi plugin
    Copyright (C) 2018 gujal

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

from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from lib import unwise
import re

class VideozUpload(ResolveUrl):
    name = 'videozupload.net'
    domains = ['videozupload.net']
    pattern = '(?://|\.)(videozupload\.net)/video/([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        headers['Referer'] = 'https://embed.videozupload.net/'
        html = response.content
        html = unwise.unwise_process(html)
        r = re.search("Clappr.+?source:\s*'([^']+)",html)
        if r:
            strurl = r.group(1) + helpers.append_headers(headers)
        else:
            raise ResolverError('File Not Found or removed')
        
        return strurl

    def get_url(self, host, media_id):
        return 'https://embed.videozupload.net/video/%s' % media_id
