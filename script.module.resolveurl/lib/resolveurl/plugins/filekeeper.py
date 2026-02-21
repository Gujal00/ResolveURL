"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal

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
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class FileKeeperResolver(ResolveUrl):
    name = 'FileKeeper'
    domains = ['filekeeper.net']
    pattern = r'(?://|\.)(filekeeper\.net)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        ref = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT}
        uri = web_url
        r = self.net.http_GET(uri, headers=headers, redirect=False)
        hdrs = r.get_headers(as_dict=True)
        location = hdrs.get('Location')
        if location:
            uri = location

        headers.update({
            'Referer': ref,
            'Origin': ref[:-1],
            'Cookie': 'lang=english; file_code={}'.format(media_id)
        })
        common.kodi.sleep(5000)
        data = {
            'op': 'download2',
            'id': media_id,
            'rand': '',
            'referer': '',
            'method_free': 'Free download',
            'down_direct': 1
        }
        src = helpers.get_redirect_url(uri, form_data=data, headers=headers)
        if src != web_url:
            headers.pop('Cookie')
            headers.pop('Origin')
            return src + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
