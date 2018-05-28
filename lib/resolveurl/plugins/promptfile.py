'''
resolveurl XBMC Addon
Copyright (C) 2013 Bstrdsmkr

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


class PromptfileResolver(ResolveUrl):
    name = "promptfile"
    domains = ["promptfile.com"]
    pattern = '(?://|\.)(promptfile\.com)/(?:l|e)/([0-9A-Za-z\-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search('''val\(['"]([^"']+)''', html)
        prefix = match.group(1) if match else ''
        data = helpers.get_hidden(html)
        for name in data:
            data[name] = prefix + data[name]

        headers['Referer'] = web_url
        html = self.net.http_POST(web_url, form_data=data, headers=headers).content
        match = re.search('''clip\s*:\s*\{.*?(?:url|src)\s*:\s*["'](?P<url>[^"']+)["']''', html, re.DOTALL)
        if not match:
            raise ResolverError('File Not Found or removed')

        source = self.net.http_GET(match.group('url'), headers=headers).get_url()
        return source + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://www.promptfile.com/l/%s' % (media_id)
