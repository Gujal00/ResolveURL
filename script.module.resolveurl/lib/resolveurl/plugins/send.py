"""
    Plugin for ResolveURL
    Copyright (C) 2021 shellc0de
                  2023 gujal

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

from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class SendResolver(ResolveUrl):
    name = 'Send'
    domains = ['send.cm', 'sendit.cloud']
    pattern = r'(?://|\.)(send(?:it)?\.(?:cm|cloud))/(?:f/embed/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        if "The file you were looking for doesn't exist." not in html:
            data = helpers.get_hidden(html)
            burl = 'https://{}'.format(host)
            url = helpers.get_redirect_url(burl, headers=headers, form_data=data)
            if url != burl:
                headers.update({'Referer': web_url})
                return url + helpers.append_headers(headers)
            else:
                raise ResolverError('Unable to locate File')
        else:
            raise ResolverError('File deleted')
        return

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://send.cm/{media_id}')
