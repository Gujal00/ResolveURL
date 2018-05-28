'''
    resolveurl XBMC Addon
    Copyright (C) 2016 Gujal

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
'''
from __resolve_generic__ import ResolveGeneric

class WatchVideoResolver(ResolveGeneric):
    name = "watchvideo"
    domains = ["watchvideo.us", "watchvideo2.us", "watchvideo3.us",
               "watchvideo4.us", "watchvideo5.us", "watchvideo6.us",
               "watchvideo7.us", "watchvideo8.us", "watchvideo9.us",
               "watchvideo10.us", "watchvideo11.us", "watchvideo12.us",
               "watchvideo13.us", "watchvideo14.us", "watchvideo15.us",
               "watchvideo16.us", "watchvideo17.us", "watchvideo18.us",
               "watchvideo19.us", "watchvideo20.us", "watchvideo21.us"]
    pattern = '(?://|\.)(watchvideo[0-9]?[0-9]?\.us)/(?:embed-)?([0-9a-zA-Z]+)'

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/{media_id}.html')
