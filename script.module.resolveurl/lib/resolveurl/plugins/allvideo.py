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

import re
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class AllVideoResolver(ResolveUrl):
    name = 'AllVideo'
    domains = ['fsst.online', 'incvideo1.online']
    pattern = r'(?://|\.)((?:fsst|incvideo\d*)\.online)/embed/(\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        response = self.net.http_GET(web_url, headers=headers)
        web_url = response.get_url()
        r = re.search(r'''file\s*:\s*["']([^"']+)''', response.content)
        if r:
            surl = r.group(1)
            if ',' in surl:
                sources = re.findall(r'''\[([^]]+)\]([^,"']+)''', surl)
                surl = helpers.pick_source(helpers.sort_sources_list(sources))
            headers.update({'Referer': web_url})
            cookie = response.get_cookies()
            if cookie:
                headers.update({'Cookie': cookie})
            return surl.rstrip('/') + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}/')
