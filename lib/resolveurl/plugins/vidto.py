"""    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
    
    Special thanks for help with this resolver go out to t0mm0, jas0npc,
    mash2k3, Mikey1234,voinage and of course Eldorado. Cheers guys :)
"""
from __resolve_generic__ import ResolveGeneric

class VidtoResolver(ResolveGeneric):
    name = "vidto"
    domains = ["vidto.me", "vidto.se"]
    pattern = '(?://|\.)(vidto\.[sm]e)/(?:embed-)?([0-9a-zA-Z]+)'
