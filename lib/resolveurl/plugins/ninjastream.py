"""
Plugin for ResolveUrl
Copyright (C) 2020 gujal

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
"""

import re
import json
from six.moves import urllib_parse
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class NinjaStreamResolver(ResolveUrl):
    name = "NinjaStream"
    domains = ['ninjastream.to']
    pattern = r'(?://|\.)(ninjastream\.to)/(?:watch|download)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content

        r = re.search(r'v-bind:stream="([^"]+)', html)
        if r:
            data = json.loads(r.group(1).replace('&quot;', '"'))
            murl = data.get('host') + data.get('hash') + '/index.m3u8'
            html = self.net.http_GET(murl, headers=headers).content
            sources = re.findall(r'RESOLUTION=\d+x(?P<label>[\d]+).*\n(?!#)(?P<url>[^\n]+)', html, re.IGNORECASE)
            if sources:
                stream_url = urllib_parse.urljoin(murl, helpers.pick_source(helpers.sort_sources_list(sources)))
                return stream_url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/watch/{media_id}')
