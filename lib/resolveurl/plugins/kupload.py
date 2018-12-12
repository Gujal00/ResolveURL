"""
    ResolveUrl site plugin
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
import re
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class KhatriResolver(ResolveUrl):
    name = "khatriuploads"
    domains = ["khatriuploads.com"]
    pattern = '(?://|\.)(khatriuploads\.com)/([0-9a-f]+)'

    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.EDGE_USER_AGENT
        self.headers = {'User-Agent': self.user_agent}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = self.headers
        response = self.net.http_GET(web_url, headers=headers)
        response_headers = response.get_headers(as_dict=True)
        cookies = response_headers.get('Set-Cookie')
        
        cookie = ''
        for ck in cookies.split('Only, '):
            cookie += ck.split(';')[0] + '; '
        headers.update({'Cookie': cookie[:-2],
                        'Referer': 'https://{}/'.format(host)})

        html = response.content
        data = helpers.get_hidden(html, index=1)
        _html = self.net.http_POST(web_url, headers=headers, form_data=data).content
        url = re.search('"link_button"\s*href="([^"]+)',_html)
        if url:
            response = self.net.http_GET(url.group(1), headers=headers)
            strurl = re.search('"link_button"\s*href="([^"]+)',response.content)
            if strurl:
                return strurl.group(1)  + helpers.append_headers(headers)        

        raise ResolverError('File not found')

    
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
