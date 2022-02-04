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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VideoMegaResolver(ResolveUrl):
    name = "videomega"
    domains = ['videomega.co']
    pattern = r'(?://|\.)(videomega\.co)/(?:e/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        response = self.net.http_GET(web_url, headers=headers).content
        t = re.search(r'var\s*token="([^"]+)', response)
        if t:
            c = re.search(r'var\s*crsf="([^"]+)', response)
            if c:
                data = {'gone': t.group(1),
                        'oujda': c.group(1)}
                headers.update({'Referer': web_url})
                post_url = 'https://www.{0}/vid/'.format(host)
                result = self.net.http_POST(post_url, form_data=data, headers=headers).content
                s = re.search(r'(http[^\s]+)', result)
                if s:
                    return s.group(1) + helpers.append_headers(headers)

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.{host}/e/{media_id}')
