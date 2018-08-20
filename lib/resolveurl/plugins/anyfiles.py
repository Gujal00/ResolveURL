"""
    Copyright (C) 2014  smokdpi

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
import urlparse
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class AnyFilesResolver(ResolveUrl):
    name = "anyfiles"
    domains = ["anyfiles.pl"]
    pattern = '(?://|\.)(anyfiles\.pl)/.*?(?:id=|v=|/)([0-9]+)'

    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.EDGE_USER_AGENT
        self.headers = {'User-Agent': self.user_agent}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        hostname = urlparse.urlparse(web_url).hostname
        self.headers['Referer'] = web_url
        response = self.net.http_GET(web_url, headers=self.headers)
        response_headers = response.get_headers(as_dict=True)
        cookie = response_headers.get('Set-Cookie')
        if cookie:
            self.headers.update({'Cookie': cookie.split(';')[0]})
        html = response.content
        for match in re.finditer('''<script[^>]*src=["']([^'"]+)''', html):
            js_html = self.__get_js(match.group(1), self.headers, hostname)
            match = re.search('''var\s+source\s*=\s*['"](http.*?mp4)''', js_html)
            if match:
                return match.group(1) + helpers.append_headers(self.headers)
        else:
            raise ResolverError('File not found')

    def __get_js(self, js_url, headers, hostname):
        js = ''
        if not js_url.startswith('http'):
            base_url = 'http://' + hostname
            js_url = urlparse.urljoin(base_url, js_url)
        
        if hostname in js_url:
            js_url = js_url.replace('&amp;', '&')
            common.logger.log('Getting JS: |%s| - |%s|' % (js_url, headers))
            js = self.net.http_GET(js_url, headers=headers).content
        return js
    
    def get_url(self, host, media_id):
        return "http://anyfiles.pl/w.jsp?id=%s&width=640&height=360&start=0&skin=0&label=false&autostart=false" % (media_id)
