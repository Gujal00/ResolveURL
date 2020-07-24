"""
    Plugin for ResolveURL
    Copyright (C) 2019 gujal

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
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.plugins.lib import helpers


class MixdropResolver(ResolveUrl):
    name = "mixdrop"
    domains = ["mixdrop.co", "mixdrop.to"]
    pattern = r'(?://|\.)(mixdrop\.[ct]o)/(?:f|e)/(\w+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Origin': 'https://{}'.format(host),
                   'Referer': 'https://{}/'.format(host),
                   'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'location\s*=\s*"([^"]+)', html)
        if r:
            web_url = 'https://{0}{1}'.format(host, r.group(1))
            html = self.net.http_GET(web_url, headers=headers).content
        if '(p,a,c,k,e,d)' in html:
            html = helpers.get_packed_data(html)
        r = re.search(r'(?:vsr|wurl|surl)[^=]*=\s*"([^"]+)', html)
        if r:
            headers = {'User-Agent': common.RAND_UA, 'Referer': web_url}
            return "https:" + r.group(1) + helpers.append_headers(headers)

        raise ResolverError("Video not found")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
