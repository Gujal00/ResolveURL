"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from six.moves import urllib_parse


class VidMolyResolver(ResolveUrl):
    name = 'VidMoly'
    domains = ['vidmoly.me', 'vidmoly.to', 'vidmoly.net']
    headers = {'User-Agent': common.RAND_UA}
    pattern = r'(?://|\.)(vidmoly\.(?:me|to|net))/(?:embed-|w/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        self.headers.update({'Referer': web_url, 'Origin': urllib_parse.urljoin(web_url, '/')[:-1]})
        html = self.net.http_GET(web_url, headers=self.headers).content

        if subs:
            subtitles = {}
            for src, label in re.findall(r'''{file:\s*"([^"]+)",\s*label:\s*"([^"]+)",\s*kind:\s*"captions"''', html, re.DOTALL):
                subtitles[label] = src if src.startswith('http') else urllib_parse.urljoin(web_url, src)

        result = helpers.scrape_sources(html, patterns=[r'''sources:\s*\[{file:"(?P<url>[^"]+)'''])
        if result:
            if subs:
                return helpers.pick_source(result, self.headers) + helpers.append_headers(self.headers), subtitles
            return helpers.pick_source(result, self.headers) + helpers.append_headers(self.headers)
        
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidmoly.net/{media_id}.html')
