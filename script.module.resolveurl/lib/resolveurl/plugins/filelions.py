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


class FileLionsResolver(ResolveGeneric):
    name = 'FileLions'
    domains = ['filelions.com', 'filelions.to', 'ajmidyadfihayh.sbs', 'alhayabambi.sbs', 'techradar.ink',
               'moflix-stream.click', 'azipcdn.com', 'mlions.pro', 'alions.pro', 'dlions.pro',
               'filelions.live', 'motvy55.store', 'filelions.xyz', 'lumiawatch.top', 'filelions.online']
    pattern = r'(?://|\.)((?:filelions|ajmidyadfihayh|alhayabambi|techradar|moflix-stream|azipcdn|motvy55|' \
              r'[mad]lions|lumiawatch)\.' \
              r'(?:com|to|sbs|ink|click|pro|live|store|xyz|top|online))/(?:v|f|d)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[r'''sources:\s*\[{file:\s*["'](?P<url>[^"']+)'''],
            generic_patterns=False,
            referer=False
        )

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}')
