"""
    Plugin for ResolveUrl
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
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class VlalaComResolver(ResolveUrl):
    name = "VlalaCom"
    domains = ["videoslala.com"]
    pattern = r'(?://|\.)(videoslala\.com)/v/([^\n]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False

        web_url = self.get_url(host, media_id)
        if not referer:
            referer = urllib_parse.urljoin(web_url, '/')

        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}

        html = self.net.http_GET(web_url, headers=headers).content
        if 'Please Wait' in html:
            raise ResolverError('Please Wait Video Uploading.')

        html = helpers.get_packed_data(html)
        sources = re.findall(r"label':\s*'(?P<label>[^']+).+?file':\s*'(?P<url>[^']+)", html)
        if sources:
            source = helpers.pick_source(sorted(sources, reverse=True))
            if source.startswith('/'):
                source = urllib_parse.urljoin(web_url, source)
            return source + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}')
