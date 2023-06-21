"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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

from resolveurl.plugins.__resolve_generic__ import ResolveGeneric


class YouDBoxResolver(ResolveGeneric):
    name = 'YouDBox'
    domains = ['youdbox.com', 'youdbox.net', 'youdbox.org', 'yodbox.com', 'youdboox.com',
               'youdbox.site']
    pattern = r'(?://|\.)(you?dboo?x\.(?:com|net|org|site))/(?:embed-)?(\w+)'
