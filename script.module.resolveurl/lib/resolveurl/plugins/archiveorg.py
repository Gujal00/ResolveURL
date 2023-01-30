"""
    Plugin for ResolveURL
    Copyright (c) 2023 gujal

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


class ArchiveResolver(ResolveUrl):
    name = 'Archive'
    domains = ['archive.org']
    pattern = r'(?://|\.)(archive\.org)/embed/([0-9a-zA-Z-_\.]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = re.findall(r'"file":"(?P<url>[^"]+)[^}]+?label":"(?P<label>[\d]+p?)', html)
        if sources:
            sources = [(x[1], x[0]) for x in sources]
            surl = 'https://' + host + helpers.pick_source(helpers.sort_sources_list(sources)).replace('/download/', '/serve/').replace(' ', '%20')
            return surl + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
