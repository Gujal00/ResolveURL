"""
    Plugin for ResolveUrl
    Copyright (C) 2015 tknorris

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

from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class TusfilesResolver(ResolveUrl):
    name = 'tusfiles'
    domains = ['tusfiles.net', 'tusfiles.com']
    pattern = r'(?://|\.)(tusfiles\.(?:net|com))/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'Origin': web_url.rsplit('/', 1)[0],
            'Referer': web_url,
            'User-Agent': common.RAND_UA
        }
        payload = {
            'op': 'download2',
            'id': media_id,
            'rand': '',
            'referer': web_url,
            'method_free': '',
            'method_premium': ''
        }
        resp = self.net.http_POST(web_url, form_data=payload, headers=headers).get_url()
        if resp != web_url:
            return resp + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
