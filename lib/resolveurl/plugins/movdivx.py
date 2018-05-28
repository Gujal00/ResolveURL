"""
    resolveurl XBMC Addon
    Copyright (C) 2012 Bstrdsmkr

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


class MovDivxResolver(ResolveUrl):
    name = "movdivx"
    domains = ["movdivx.com", "divxme.com", "streamflv.com"]
    pattern = '(?://|\.)((?:movdivx|divxme|streamflv)\.com)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        cookie = response.get_headers(as_dict=True).get('Set-Cookie', '')
        if cookie:
            headers.update({'Cookie': cookie})
        html = response.content
        
        if html:
            data = helpers.get_hidden(html)
            if not "method_free" in data: data.update({'method_free': 'Submit Query'})
            _html = self.net.http_POST(web_url, headers=headers, form_data=data).content
            if _html:
                sources = helpers.scrape_sources(_html, patterns=['''file:\s*["'](?P<url>[^"']+)'''])
                if sources: return helpers.pick_source(sources) + helpers.append_headers(headers)
                
        raise ResolverError("Video not found")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://streamflv.com/{media_id}')
