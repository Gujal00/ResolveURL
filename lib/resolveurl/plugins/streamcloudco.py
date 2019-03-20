"""
streamcloud.co resolveurl plugin
Copyright (C) 2018 xxxxxx

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from __resolve_generic__ import ResolveGeneric


class StreamcloudcoResolver(ResolveGeneric):
    name = "streamcloudco"
    domains = ["streamcloud.co"]
    pattern = '(?://|\.)(streamcloud\.co)/(?:embed[/-])?([0-9A-Za-z]+)'
    
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/embed/{media_id}')
