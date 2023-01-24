"""
    Plugin for ResolveURL
    Copyright (C) 2022 gujal

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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class FastUploadResolver(ResolveUrl):
    name = 'FastUpload'
    domains = ['fastupload.io']
    pattern = r'(?://|\.)(fastupload\.io)/(?:en|es|de)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        rurl = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers=headers).content

        r = re.search(r'name="csrf-token"\s*content="([^"]+)', html)
        if r:
            headers.update({
                'X-CSRF-TOKEN': r.group(1),
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': rurl[:-1]
            })
            shtml = json.loads(self.net.http_POST(self.get_dlurl(host, media_id), form_data=True, headers=headers, jdata=True).content)
            source = shtml.get('download_link')
            if source:
                headers.pop('X-Requested-With')
                return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/en/{media_id}/file')

    def get_dlurl(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}/download/create')
