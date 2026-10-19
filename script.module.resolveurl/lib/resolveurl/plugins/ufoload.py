"""
    Plugin for ResolveURL
    Copyright (C) 2026 TempleLain

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

import json
import re
from six.moves import urllib_parse, urllib_error
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class UFOloadResolver(ResolveUrl):
    name = 'UFOload'
    domains = ['ufoload.com', 'iframe.andromedans.live']
    pattern = r'(?://|\.)(ufoload\.com|iframe\.andromedans\.live)/(?:e|embed|v)/([0-9a-zA-Z_-]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': urllib_parse.urljoin(web_url, '/')
        }
        try:
            html = self.net.http_GET(web_url, headers=headers).content
        except urllib_error.HTTPError:
            # removed files and unknown ids get a 404 page
            raise ResolverError('File Not Found or Removed')
        # Nuxt app: the signed links come with the server rendered payload (__NUXT_DATA__),
        # an object with playback (hls master) and renditions (mp4 per quality)
        r = re.search(r'<script[^>]+id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if r:
            data = json.loads(r.group(1))

            def val(i):
                # values are referenced by their index in the payload list,
                # negative numbers mark undefined and the like
                return data[i] if isinstance(i, int) and 0 <= i < len(data) else None

            links = next((x for x in data if isinstance(x, dict) and 'playback' in x and 'renditions' in x), None)
            if links:
                renditions = val(links.get('renditions'))
                sources = [(q, val(i)) for q, i in renditions.items()] if isinstance(renditions, dict) else []
                sources = helpers.sort_sources_list([s for s in sources if s[1]])
                # the mp4 files carry only the default audio track, the hls master
                # has all audio and subtitle tracks and stays selectable after them
                if val(links.get('playback')):
                    sources.append(('HLS', val(links.get('playback'))))
                if sources:
                    return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
