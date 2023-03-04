"""
    Plugin for ResolveURL
    Copyright (C) 2023 groggyegg

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

from six.moves.urllib_parse import unquote

from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.lib.base64shim import base64_decode
from resolveurl.resolver import ResolverError, ResolveUrl


class DubokuResolver(ResolveUrl):
    name = 'Duboku'
    domains = ['duboku.ru', 'duboku.tv']
    pattern = r'(?://|\.)(duboku\.(?:ru|tv))/((?:video|vodplay)/\d+-\d+-\d+\.html)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'"encrypt":(\d),.+?,"url":"([^"]+)","url_next":"([^"]+)"', html)

        if match:
            encrypt, url, url_next = match.groups()

            if encrypt == '1':
                url = unquote(url)
                url_next = unquote(url_next)
            elif encrypt == '2':
                url = unquote(base64_decode(url))
                url_next = unquote(base64_decode(url_next))
            else:
                url = url.replace('\\/', '/')
                url_next = url_next.replace('\\/', '/')
        else:
            raise ResolverError('Unable to locate script')

        if url.startswith('http'):
            return url + helpers.append_headers(headers)
        else:
            return url_next + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
