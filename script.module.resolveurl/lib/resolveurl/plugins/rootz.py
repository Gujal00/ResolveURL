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

import json
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class RootzResolver(ResolveUrl):
    name = 'Rootz'
    domains = ['rootz.so', 'www.rootz.so']
    pattern = r'(?://|\.)(rootz\.so)/d/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': ref}
        html = self.net.http_GET(web_url, headers=headers).content
        r = json.loads(html)
        if r.get('success'):
            headers.update({'Referer': ref, 'Origin': ref[:-1]})
            url = r.get('data').get('url') + helpers.append_headers(headers)
            return url

        raise ResolverError("Unable to locate stream URL.")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/api/files/download-by-short/{media_id}')
