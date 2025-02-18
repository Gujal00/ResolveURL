"""
    Plugin for ResolveURL
    Copyright (C) 2025 Peter3344

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
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric


class ForaFileResolver(ResolveGeneric):
    name = 'ForaFile'
    domains = ['forafile.com', 'asjp1j93c1.sbs', 'cd189Tryo7.sbs']
    pattern = r'(?://|\.)((?:forafile|asjp1j93c1|cd189Tryo7)\.(?:com|sbs))/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[r'''file:\s*['"](?P<url>[^'"]+)'''],
            generic_patterns=False,
            referer=False
        )

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
