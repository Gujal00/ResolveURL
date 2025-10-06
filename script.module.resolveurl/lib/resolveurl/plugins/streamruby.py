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
    domains = ['streamruby.com', 'sruby.xyz', 'rubystream.xyz', 'tuktukcimamulti.buzz',
               'stmruby.com', 'rubystm.com', 'rubyvid.com', 'kinoger.be']
    pattern = r'(?://|\.)((?:s?(?:tream|tm)?ruby(?:stream|stm|vid)?|kinoger|tuktukcimamulti)\.' \
              r'(?:com|xyz|buzz|be))/(?:embed-|e/|d/)?(\w+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Accept-Language': 'en-US,en;q=0.5'}
        html = self.net.http_GET(web_url, headers=headers).content
        html += helpers.get_packed_data(html)
        master_url = re.search(r'''sources:\s*\[(?:{src:|{file:)?\s*['"]([^'"]+)''', html)
        if master_url:
            rurl = 'https://{}/'.format(host)
            headers.update({'Origin': rurl[:-1], 'Referer': rurl})
            stream_url = master_url.group(1) + helpers.append_headers(headers)
            if subs:
                subtitles = helpers.scrape_subtitles(html, web_url)
                return stream_url, subtitles
            return stream_url

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
