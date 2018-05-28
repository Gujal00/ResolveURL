"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
import json
import base64
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class FlixtorResolver(ResolveUrl):
    name = "flixtor"
    domains = ['flixtor.to']
    pattern = '(?://|\.)(flixtor\.to)/watch/([\w/\-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        referer = 'https://flixtor.to/watch/%s' % media_id
        headers = {'User-Agent': common.RAND_UA}
        response = self.net.http_GET(referer, headers=headers)
        response_headers = response.get_headers(as_dict=True)
        headers.update({'Referer': referer})
        cookie = response_headers.get('Set-Cookie', None)
        if cookie:
            headers.update({'Cookie': cookie.replace('HttpOnly, ', '')})
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            try:
                html = base64.b64decode(html.decode("rot13"))
                l_ = []
                for c_ in html:
                    k_ = ord(c_)
                    t_ = chr(33 + (k_ + 14) % 94) if 33 <= k_ <= 126 else chr(k_)
                    l_.append(t_)
                html = ''.join(l_)
                html = json.loads(html)
            except Exception as e:
                raise ResolverError(e)

            source = html.get("file", None)
            if source:
                return source + helpers.append_headers(headers)

        raise ResolverError("Unable to locate video")

    def get_url(self, host, media_id):
        if media_id.lower().startswith("tv/"):
            url = 'https://flixtor.to/ajax/gvid/e'
        else:
            url = 'https://flixtor.to/ajax/gvid/m'
        media_id = re.sub('/{2,}', '/', re.sub('[^\d/]', '', media_id))
        media_id = media_id[:-1] if media_id.endswith('/') else media_id

        return self._default_get_url(host, media_id, template=url + media_id)
