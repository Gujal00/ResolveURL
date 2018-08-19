"""
    resolveurl XBMC Addon
    Copyright (C) 2018 jsergio

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
import re
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class UnitPlayResolver(ResolveUrl):
    name = "unitplay"
    domains = ["unitplay.net"]
    pattern = '(?://|\.)(unitplay\.net)/tt([0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            player_id = re.search('''SvplayerID\|([a-z0-9]+)''', html, re.I)
            if player_id:
                player_url = 'https://unitplay.net//CallPlayer'
                data = {'id': player_id.group(1)}
                headers.update({'Referer': web_url})
                _html = self.net.http_POST(player_url, data, headers=headers).content
                if _html:
                    _html = _html.decode("hex")
                    sources = helpers.scrape_sources(_html)
                    if sources:
                        return helpers.pick_source(sources) + helpers.append_headers(headers)
                
        raise ResolverError("Unable to locate video")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/tt{media_id}')
