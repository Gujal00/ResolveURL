"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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


class xHamsterResolver(ResolveGeneric):
    name = 'xhamster'
    domains = ['xhamster.com', 'xhamster.desi']
    domains += ['xhamster{0}.com'.format(x) for x in range(1, 50)]
    domains += ['xhamster{0}.desi'.format(x) for x in range(1, 25)]
    pattern = r'(?://|\.)(xhamster\d{0,2}\.(?:com|desi))/.+[/\-=](\w+)'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[r'''{"url":"(?P<url>http[^"]+)[^}]+label":"(?P<label>[^"]+)'''],
            generic_patterns=False,
            result_blacklist=["1080p"]
        )

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
