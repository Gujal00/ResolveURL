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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class UperBoxResolver(ResolveUrl):
    name = 'UperBox'
    domains = ['www.uperbox.net']
    pattern = r'(?://|\.)(www\.uperbox\.net)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': 'https://{0}/'.format(host)
        }
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'href="([^"]+)"\s*class="btn', html)
        if r:
            durl = urllib_parse.urljoin(web_url, r.group(1))
            res = self.net.http_GET(durl, headers=headers).content
            s = re.search(r'href="([^"]+)"\s*class="btn', res)
            if s:
                surl = urllib_parse.urljoin(web_url, s.group(1))
                common.kodi.sleep(4000)
                url = helpers.get_redirect_url(surl.replace('&amp;', '&'), headers=headers)
                if url != surl:
                    return url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
