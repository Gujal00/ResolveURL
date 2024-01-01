"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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

import json
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamGzzzResolver(ResolveUrl):
    name = 'StreamGzzz'
    domains = ['streamgzzz.com']
    pattern = r'(?://|\.)(streamgzzz\.com)/video/([0-9a-zA-Z$:/.]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://{0}'.format(host)
        }
        payload = {'hash': media_id}
        if referer:
            payload.update({'r': referer})
        html = self.net.http_POST(web_url, form_data=payload, headers=headers).content
        html = json.loads(html)
        source = html.get('securedLink')
        if source:
            headers.pop('X-Requested-With')
            return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}&do=getVideo')
