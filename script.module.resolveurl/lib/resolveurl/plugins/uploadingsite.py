"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class UploadingSiteResolver(ResolveUrl):
    name = 'UploadingSite'
    domains = ['uploadingsite.com']
    pattern = r'(?://|\.)(uploadingsite\.com)/([0-9a-zA-Z]+)'

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
        url = helpers.get_redirect_url(web_url, headers=headers, form_data=payload)
        if url != web_url:
            headers['verifypeer'] = 'false'
            return url.replace(' ', '%20').replace('http:', 'https:') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
