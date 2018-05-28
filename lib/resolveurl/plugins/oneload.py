'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import re
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class OneloadResolver(ResolveUrl):
    name = "oneload"
    domains = ["oneload.co", "oneload.com"]
    pattern = "(?://|\.)(oneload\.(?:co|com))/([a-zA-Z0-9]+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        form_data = {'op': 'download2', 'id': media_id, 'rand': '', 'referer': web_url, 'method_free': 'Free Download', 'method_premium': '', 'adblock_detected': '0'}
        html = self.net.http_POST(web_url, form_data=form_data, headers=headers).content
        
        if html:
            source = re.search(r"""href=["'](.+?oneload.co:\d+/d/\w+/([^"']+)).+?>\2</a>""", html)
            if source: return source.group(1) + helpers.append_headers(headers)
                
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://oneload.co/{media_id}')
