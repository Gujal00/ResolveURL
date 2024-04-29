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

from resolveurl.lib import helpers
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric
from six.moves import urllib_parse


class FileLionsResolver(ResolveGeneric):
    name = 'FileLions'
    domains = ['filelions.com', 'filelions.to', 'ajmidyadfihayh.sbs', 'alhayabambi.sbs',
               'moflix-stream.click', 'azipcdn.com', 'mlions.pro', 'alions.pro', 'dlions.pro',
               'filelions.live', 'motvy55.store', 'filelions.xyz', 'lumiawatch.top', 'filelions.online',
               'javplaya.com', 'fviplions.com', 'egsyxutd.sbs', 'filelions.site', 'filelions.co',
               'vidhide.com', 'vidhidepro.com', 'vidhidevip.com', 'javlion.xyz', 'fdewsdc.sbs',
               'techradar.ink', 'anime7u.com', 'coolciima.online', 'gsfomqu.sbs']
    pattern = r'(?://|\.)((?:filelions|ajmidyadfihayh|alhayabambi|techradar|moflix-stream|azipcdn|motvy55|' \
              r'[mad]lions|lumiawatch|javplaya|javlion|fviplions|egsyxutd|fdewsdc|vidhide(?:pro|vip)?|' \
              r'anime7u|coolciima|gsfomqu)' \
              r'\.(?:com?|to|sbs|ink|click|pro|live|store|xyz|top|online|site))/(?:s|v|f|d|embed)/([0-9a-zA-Z$:/.]+)'

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
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}')
