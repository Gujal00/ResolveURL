"""
    Plugin for ResolveUrl
    Copyright (C) 2021 ADDON-LAB, KAR10S

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class MegaupNetResolver(ResolveUrl):
    name = 'megaupnet'
    domains = ['megaup.net']
    pattern = r'(?://|\.)(megaup\.net)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        if 'FILE NOT FOUND' not in html:
            r = re.search(r"btn-default'\s*href='([^']+)", html)
            if r:
                headers.update({'Referer': web_url})
                common.kodi.sleep(7000)
                strurl = helpers.get_redirect_url(r.group(1), headers=headers)
                if strurl:
                    return strurl + helpers.append_headers(headers)
        raise ResolverError('File cannot be located or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}/')
