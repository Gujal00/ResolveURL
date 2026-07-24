"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class FireStreamResolver(ResolveUrl):
    name = 'FireStream'
    domains = ['firestream.to']
    pattern = r'(?://|\.)(firestream\.to)/(?:e|v)/([0-9a-zA-Z_]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search('id="token-blob"[^>]+>([^<]+)', html)
        if r:
            pdata = {'blob': r.group(1)}
            headers.update({'Referer': ref, 'Origin': ref[:-1]})
            api_url = self.get_api_url(host, media_id)
            jd = self.net.http_POST(api_url, form_data=pdata, headers=headers, jdata=True).json
            if jd.get('signedVideoUrl'):
                return jd.get('signedVideoUrl') + helpers.append_headers(headers)

        raise ResolverError("Unable to locate stream URL.")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')

    def get_api_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/api/videos/{media_id}/resolve')
