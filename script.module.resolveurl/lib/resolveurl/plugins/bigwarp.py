"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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


class BigWarpResolver(ResolveUrl):
    name = 'BigWarp'
    domains = ['bigwarp.io', 'bgwp.cc', 'bigwarp.art', 'bigwarp.cc']
    pattern = r'(?://|\.)((?:bigwarp|bgwp)\.(?:io|cc|art))/(?:e/|embed-)?([0-9a-zA-Z=]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = re.findall(r'''file\s*:\s*['"](?P<url>[^'"]+)['"],\s*label\s*:\s*['"](?P<label>\d+p?)''', html)
        if sources:
            sources = [(x[1], x[0]) for x in sources]
            surl = helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)
            if subs:
                subtitles = helpers.scrape_subtitles(html, web_url)
                return surl, subtitles
            return surl
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
