"""
Watchpass resolveurl XBMC Addon
Copyright (C) 2016 Seberoth

Version 0.0.1

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
import re
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class WatchpassResolver(ResolveUrl):
    name = "everplay.watchpass.net"
    domains = ['everplay.watchpass.net']
    pattern = '(?://|\.)(everplay\.watchpass\.net)/se/rapidme\.php\?url=(.+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content

        r = re.search('file: "(.+?)",', html)
        if r:
            return r.group(1)
        else:
            raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/se/rapidme.php?url={media_id}')
