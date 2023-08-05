"""
    Plugin for ResolveURL
    Copyright (C) 2023 shellc0de

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

from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric


class StreamWishResolver(ResolveGeneric):
    name = 'StreamWish'
    domains = ['streamwish.com', 'streamwish.to', 'ajmidyad.sbs', 'khadhnayad.sbs', 'yadmalik.sbs',
               'hayaatieadhab.sbs', 'kharabnahs.sbs', 'atabkhha.sbs', 'atabknha.sbs', 'atabknhk.sbs',
               'atabknhs.sbs', 'abkrzkr.sbs', 'abkrzkz.sbs', 'wishembed.pro', 'mwish.pro',
               'awish.pro', 'dwish.pro', 'vidmoviesb.xyz', 'embedwish.com']
    pattern = r'(?://|\.)((?:streamwish|ajmidyad|khadhnayad|yadmalik|hayaatieadhab|kharabnahs|' \
              r'atabkhha|atabknha|atabknhk|atabknhs|abkrzkr|abkrzkz|wishembed|[mad]wish|vidmoviesb|' \
              r'embedwish)' \
              r'\.(?:com|to|sbs|pro|xyz))/(?:e/|f/)?([0-9a-zA-Z$:/.]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[r'''sources:\s*\[{file:\s*["'](?P<url>[^"']+)'''],
            generic_patterns=False,
            referer=referer
        )

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
