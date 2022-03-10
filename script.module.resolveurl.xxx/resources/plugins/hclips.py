"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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

import json
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class HClipsResolver(ResolveUrl):
    name = 'hclips'
    domains = ['hclips.com']
    pattern = r'(?://|\.)(hclips\.com)/(?:videos|embed)/(\d+)'

    def get_media_url(self, host, media_id):
        headers = {'Referer': 'https://{}/'.format(host),
                   'User-Agent': common.RAND_UA}
        web_url = self.get_url(host, media_id)
        r = self.net.http_GET(web_url, headers=headers)
        jdata = json.loads(r.content)[0]
        if jdata.get('video_url'):
            source = 'https://{}{}'.format(host, self._decode(jdata.get('video_url')))
            return source + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(
            host, media_id, template='https://{host}/api/videofile.php?video_id={media_id}&lifetime=8640000'
        )

    def _decode(self, e):
        LUT = {u'\u0410': 'A', u'\u0412': 'B', u'\u0421': 'C', u'\u0415': 'E', u'\u041c': 'M'}
        e = ''.join([x if ord(x) < 128 else LUT[x] for x in e])
        t = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~'
        i = ''
        a = 0
        while a < len(e):
            n = t.index(e[a])
            o = t.index(e[a + 1])
            s = t.index(e[a + 2])
            r = t.index(e[a + 3])
            a += 4
            n = n << 2 | o >> 4
            o = (15 & o) << 4 | s >> 2
            l = (3 & s) << 6 | r
            i += chr(n)
            if s != 64:
                i += chr(o)
            if r != 64:
                i += chr(l)
        return i

    @classmethod
    def _is_enabled(cls):
        return True
