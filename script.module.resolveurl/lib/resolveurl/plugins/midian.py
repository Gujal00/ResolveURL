"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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

from resolveurl.resolver import ResolveUrl


class MidianResolver(ResolveUrl):
    name = 'Midian'
    domains = ['midian.appboxes.co']
    pattern = r'(?://|\.)(midian\.appboxes\.co)/(.+)'

    def get_media_url(self, host, media_id):
        # Kotlin resolver just ensures https and passes through
        return 'https://{}/{}'.format(host, media_id)

    def get_url(self, host, media_id):
        return 'https://{}/{}'.format(host, media_id)
