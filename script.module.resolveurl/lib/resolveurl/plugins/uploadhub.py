"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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


class UploadHubResolver(ResolveUrl):
    name = 'UploadHub'
    domains = ['uploadhub.wf']
    pattern = r'(?://|\.)(uploadhub\.wf)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        r = self.net.http_GET(web_url, headers=headers)
        surl = r.get_url()
        payload = helpers.get_hidden(r.content)
        if not payload:
            raise ResolverError('File Removed')
        ref = urllib_parse.urljoin(web_url, '/')
        headers.update({'Origin': ref[:-1], 'Referer': ref})
        html = self.net.http_POST(surl, form_data=payload, headers=headers).content
        source = re.search(r'''class="downld">\s*<a\s*href="([^"]+)''', html)
        if source:
            headers.update({'verifypeer': 'false'})
            return source.group(1).replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError('File Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
