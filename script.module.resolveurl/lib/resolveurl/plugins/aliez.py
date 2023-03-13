"""
    Plugin for ResolveURL
    Copyright (C) 2011 t0mm0

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
from resolveurl.lib import helpers
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric


class AliezResolver(ResolveGeneric):
    name = 'Aliez'
    domains = ['aliez.me']
    pattern = r'(?://|\.)(aliez\.me)/(?:(?:player/video\.php\?id=([0-9]+)&s=([A-Za-z0-9]+))|(?:video/([0-9]+)/([A-Za-z0-9]+)))'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[r'''file:\s*['"](?P<url>[^'"]+)'''],
            generic_patterns=False
        ).replace(' ', '%20')

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url, re.I)
        if r:
            r = list(filter(None, r.groups()))
            r = [r[0], '%s|%s' % (r[1], r[2])]
            return r
        else:
            return False

    def get_url(self, host, media_id):
        media_id = media_id.split('|')
        return self._default_get_url(host, media_id, template='http://emb.apl215.me/player/video.php?id=%s&s=%s&w=590&h=332' % (media_id[0], media_id[1]))
