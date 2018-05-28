'''
    resolveurl XBMC Addon
    Copyright (C) 2016 Gujal

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
'''
from __resolve_generic__ import ResolveGeneric

class SpeedPlayResolver(ResolveGeneric):
    name = "speedplay.xyz"
    domains = ["speedplay.xyz", "speedplay.us", "speedplay1.site",
               "speedplay.pw", "speedplay1.pw", "speedplay3.pw", 
               "speedplayy.site", "speedplay.pro"]
    pattern = '(?://|\.)(speedplay[0-9a-z]?\.(?:us|xyz|pw|site|pro))/(?:embed-)?([0-9a-zA-Z]+)'
