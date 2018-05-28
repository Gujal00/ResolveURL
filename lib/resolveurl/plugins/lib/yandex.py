'''
    resolveurl XBMC Addon
    Copyright (C) 2017 jsergio

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
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class YandexResolver(ResolveUrl):
    name = 'yandex'
    domains = ['disk.yandex.ru', 'yadi.sk']
    pattern = '(?://|\.)((?:yadi\.sk|disk\.yandex\.ru))/i/([\w\-]+)'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(self.get_url(host, media_id),
                                     patterns=['''dimension":\s*"(?P<label>[\d]{3,4}p?)".+?"url":\s*"(?P<url>[^"]+)'''],
                                     generic_patterns=False).replace(' ', '%20')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://yadi.sk/i/{media_id}')
