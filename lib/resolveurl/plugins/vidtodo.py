"""
    Kodi resolveurl plugin
    Copyright (C) 2016  script.module.resolveurl

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

class VidToDoResolver(ResolveUrl):
    name = 'vidtodo'
    domains = ['vidtodo.com', 'vidtodo.me']
    pattern = '(?://|\.)(vidtodo\.(?:com|me))/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            data = helpers.get_hidden(html)
            headers.update({'Referer': web_url})
            common.kodi.sleep(2000)
            _html = self.net.http_POST(web_url, headers=headers, form_data=data).content
            if _html:
                sources = helpers.scrape_sources(_html, patterns=['''(?:file:|xpro\()\s*["'](?P<url>[^"']+)["']\)?,\s*label\s*:\s*["'](?P<label>[^"',]{3,4})["']'''], generic_patterns=False)
                if sources:
                    sources = [(source[0], source[1].decode("rot-13")) if (source[1].startswith("uggc")) else (source[0], source[1]) for source in sources]

                    return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
