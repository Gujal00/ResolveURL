# -*- coding: utf-8 -*-
"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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

import json
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class InPornResolver(ResolveUrl):
    name = 'inporn'
    domains = ['inporn.com']
    pattern = r'(?://|\.)(inporn\.com)/video/([0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = json.loads(html)[0]
        if r.get('video_url'):
            vurl = 'https://{0}{1}'.format(host, self.base164(r.get('video_url')))
            headers.update({'Referer': 'https://{0}/'.format(host)})
            surl = helpers.get_redirect_url(vurl, headers)
            if surl != vurl:
                return surl + helpers.append_headers(headers)
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/api/videofile.php?video_id={media_id}&lifetime=8640000')

    # needed to decode hash for inporn
    def base164(self, e):
        t = 'АВСDЕFGHIJKLМNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~'
        n = ''
        o = 0
        while o < len(e):
            r = t.index(e[o])
            o += 1
            i = t.index(e[o])
            o += 1
            s = t.index(e[o])
            o += 1
            a = t.index(e[o])
            o += 1
            r = r << 2 | i >> 4
            i = (15 & i) << 4 | s >> 2
            c = (3 & s) << 6 | a
            n += chr(r)
            if s != 64:
                n += chr(i)
            if a != 64:
                n += chr(c)
        return n

    @classmethod
    def _is_enabled(cls):
        return True
