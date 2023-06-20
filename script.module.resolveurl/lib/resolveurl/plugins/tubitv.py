"""
    Plugin for ResolveURL
    Copyright (C) 2011 t0mm0

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
import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class TubiTvResolver(ResolveUrl):
    name = 'TubiTV'
    domains = ['tubitv.com']
    pattern = r'(?://|\.)(tubitv\.com)/(?:video|embed|movies)/(\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content

        r = re.search(r"""window\.__data\s*=\s*({.+?});""", html)
        if r:
            data = re.sub(r'undefined', '""', r.group(1))
            data = re.sub(r'new\s[^,]+', '""', data)
            data = json.loads(data)
            stream_url = data["video"]["byId"][media_id]["url"].replace(r"\\u002F", "/")
            if stream_url.startswith("//"):
                stream_url = "https:%s" % stream_url
            headers.update({"Referer": web_url})
            return stream_url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
