'''
Plugin for ResolveURL
Copyright (C) 2018 bugatsinho

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

import re
from lib import helpers
from lib import jsunpack
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamvidResolver(ResolveUrl):
    name = "streamvid"
    domains = ["streamvid.co"]
    pattern = '(?://|\.)(streamvid\.co)/player/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.findall(r'JuicyCodes.Run\(([^\)]+)', html, re.IGNORECASE)

        if r:
            Juice = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            e = re.sub(r'\"\s*\+\s*\"', '', r[-1])
            e = re.sub(r'[^A-Za-z0-9+\\/=]', '', e)

            t = ""
            n = r = i = s = o = u = a = f = 0

            while f < len(e):
                try:
                    s = Juice.index(e[f]);
                    f += 1;
                    o = Juice.index(e[f]);
                    f += 1;
                    u = Juice.index(e[f]);
                    f += 1;
                    a = Juice.index(e[f]);
                    f += 1;
                    n = s << 2 | o >> 4;
                    r = (15 & o) << 4 | u >> 2;
                    i = (3 & u) << 6 | a
                    t += chr(n)
                    if 64 != u: t += chr(r)
                    if 64 != a: t += chr(i)
                except:
                    continue
                pass

            try:
                t = jsunpack.unpack(t)
                t = unicode(t, 'utf-8')
            except:
                t = None

            sources = helpers.scrape_sources(t)

            headers.update({'Range': 'bytes=0-'})
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/{media_id}/')
