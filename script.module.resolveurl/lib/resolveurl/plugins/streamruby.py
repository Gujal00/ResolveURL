"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamRubyResolver(ResolveUrl):
    name = 'StreamRuby'
    domains = ['streamruby.com', 'sruby.xyz', 'rubystream.xyz']
    pattern = r'(?://|\.)(s?(?:tream)?ruby(?:stream)?\.(?:com|xyz))/(?:embed-|e/|d/)?(\w+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        html += helpers.get_packed_data(html)
        master_url = re.search(r'''sources:\s*\[(?:{src:|{file:)?\s*['"]([^'"]+)''', html)
        if master_url:
            rurl = 'https://{}/'.format(host)
            headers.update({'Origin': rurl[:-1], 'Referer': rurl})
            master_html = self.net.http_GET(master_url.group(1), headers=headers).content
            sources = re.findall(r'[A-Z]{10}=\d+x(?P<label>[\d]+).+\n(?!#)(?P<url>[^\n]+)', master_html)
            if sources:
                return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
