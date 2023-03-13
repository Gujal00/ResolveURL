"""
    Plugin for ResolveURL
    Copyright (c) 2022 gujal

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

from resolveurl.plugins.__resolve_generic__ import ResolveGeneric
from resolveurl.lib import helpers


class AnonFilesResolver(ResolveGeneric):
    name = 'AnonFiles'
    domains = ['anonfiles.com', 'bayfiles.com']
    pattern = r'(?://|\.)((?:bay|anon)files\.com)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[r'(?s)id="download-url".+?href="(?P<url>[^"]+)'],
            generic_patterns=False,
            referer=False,
            result_blacklist=['.zip', '.rar', '.7z']
        ).replace(' ', '%20').replace('https:', 'http:')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
