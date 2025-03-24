"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class WootlyResolver(ResolveUrl):
    name = 'Wootly'
    domains = ['www.wootly.ch']
    pattern = r'(?://|\.)(www\.wootly\.ch)/\?v=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        resp1 = self.net.http_GET(web_url, headers=headers)
        ref = urllib_parse.urljoin(web_url, '/')
        r = re.search(r'<iframe.+?src="([^"]+)', resp1.content)
        if r:
            cookiestr = resp1.get_headers(as_dict=True).get('Set-Cookie', '').split(';')[0]
            headers.update({'Referer': web_url, 'Cookie': cookiestr})
            data = {'qdfx': 1}
            headers.update({'Origin': ref[:-1], 'Cookie': cookiestr})
            html = self.net.http_POST(r.group(1), form_data=data, headers=headers).content
            tk = re.search(r'tk="([^"]+)', html)
            vd = re.search(r'vd="([^"]+)', html)
            c = re.search(r',\s*c="([^"]+)', html)
            if all([tk, vd, c]):
                url2 = urllib_parse.urljoin(r.group(1), c.group(1))
                params = {'t': tk.group(1), 'id': vd.group(1)}
                url2 += '?{0}'.format(urllib_parse.urlencode(params))
                headers.pop('Origin')
                resp = self.net.http_GET(url2, headers=headers).content
                if resp:
                    resp2 = True
                    headers = {'Referer': ref, 'User-Agent': common.RAND_UA}
                    while '.mp4' not in resp and resp2:
                        resp2 = helpers.get_redirect_url(resp, headers=headers)
                        if resp2 == resp:
                            resp2 = False
                            break
                        else:
                            resp = resp2
                            resp2 = True

                    if resp2:
                        return resp + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/?v={media_id}')
