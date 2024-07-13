"""
    Plugin for ResolveURL
    Copyright (C) 2024 MrDini123 (github.com/movieshark)

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


class AmdaHostResolver(ResolveGeneric):
    name = 'AmdaHost'
    domains = ['amdahost.com']
    pattern = r'(?://|\.)(amdahost\.com)/watch(?:_direct)?.php\?id=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        return helpers.get_media_url(
            self.get_url(host, media_id),
            referer=True,
            patterns=[r'''id="myVideo.+?data-src="(?P<url>[^"]+)''',
                      r'''<source[^>]+?src="(?P<url>[^"]+)'''],
            generic_patterns=False,
            subs=subs
        )

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/watch.php?id={media_id}')
