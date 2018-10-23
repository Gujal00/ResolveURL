'''
    resolveurl Kodi plugin
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
'''
import re
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class TVLogyResolver(ResolveUrl):
    name = "tvlogy.to"
    domains = ["tvlogy.to"]
    pattern = '(?://|\.)(tvlogy\.to)/(?:embed/|watch\.php\?v=)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if 'Not Found' in html:
            raise ResolverError('File Removed')

        if 'Video is processing' in html:
            raise ResolverError('File still being processed')

        packed = re.search("JuicyCodes\.Run\((.+?)\)", html, re.I)
        if packed:
            from base64 import b64decode
            packed = packed.group(1).replace('"', '').replace('+', '')
            packed = b64decode(packed)
            html += '%s</script>' % packed.strip()

        sources = helpers.scrape_sources(html)
        if sources:
            headers.update({'Referer': web_url, 'Range': 'bytes=0-'})
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
