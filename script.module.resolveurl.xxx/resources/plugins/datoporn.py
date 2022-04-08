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
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class DatoPornResolver(ResolveUrl):
    name = "datoporn"
    domains = ['datoporn.com', 'dato.porn', 'datoporn.co']
    pattern = r'(?://|\.)(datoporn\.com|dato\.porn|datoporn\.co)/(?:embed[/-]|videos/|emb.html\?)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        alt_url = re.search(r"video_alt_url:\s*'([^']+)", html)
        if alt_url:
            alt_url = alt_url.group(1)
            if alt_url.startswith('http'):
                html = self.net.http_GET(alt_url, headers=headers).content

        sources = re.findall(r"video(?:_alt)?_url:\s*'(?P<url>[^']+).+?text:\s*'(?P<label>[^']+)", html)
        if sources:
            sources = [(label, url) for url, label in sources]
            url = helpers.pick_source(helpers.sort_sources_list(sources))
            if url.startswith('function/'):
                lcode = re.findall(r"license_code:\s*'([^']+)", html)[0]
                url = helpers.fun_decode(url, lcode)
            return url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.datoporn.com/embed/{media_id}/')

    @classmethod
    def _is_enabled(cls):
        return True
