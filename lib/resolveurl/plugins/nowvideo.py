"""
    resolveurl Kodi plugin
    Copyright (C) 2011 t0mm0
    Updated by Gujal (C) 2016

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

from __resolve_generic__ import ResolveGeneric

class NowvideoResolver(ResolveGeneric):
    name = "nowvideo"
    domains = ['nowvideo.eu', 'nowvideo.ch', 'nowvideo.sx', 'nowvideo.co', 'nowvideo.li', 'nowvideo.fo', 'nowvideo.at', 'nowvideo.ec']
    pattern = '(?://|\.)(nowvideo\.(?:eu|ch|sx|co|li|fo|at|ec))/(?:video/|embed\.php\?\S*v=|embed/\?v=)([A-Za-z0-9]+)'

    def get_url(self, host, media_id):
        return 'http://embed.nowvideo.sx/embed/?v=%s' % media_id
