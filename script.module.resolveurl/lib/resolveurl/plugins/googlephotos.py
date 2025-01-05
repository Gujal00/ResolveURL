"""
    Plugin for ResolveURL
    Copyright (C) 2024 MrDini123 (github.com/movieshark)

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
from random import choice
from string import ascii_letters, digits
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class GooglePhotosResolver(ResolveUrl):
    name = 'GooglePhotos'
    domains = ['photos.google.com', 'photos.app.goo.gl']
    pattern = r'(?://|\.)(photos\.google\.com|photos\.app\.goo\.gl)/((?:share/)?(?:[0-9a-zA-Z_?=\-\/]+))'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT}
        r = self.net.http_GET(web_url, headers=headers, redirect=False)
        if r.get_redirect_url():
            web_url = r.get_redirect_url()
            r = self.net.http_GET(web_url, headers=headers).content
        else:
            r = r.content
        f_url = re.search(r'<a\s+class="[^"]*"\s+tabindex="0"\s+jsaction="click:[^"]*"\s+href="([^"]+)"', r)
        if f_url:
            f_url = f_url.group(1)
            if f_url.startswith('.'):
                f_url = urllib_parse.urljoin(web_url, f_url[1:])
            elif f_url.startswith('/'):
                f_url = urllib_parse.urljoin(web_url, f_url)
            r = self.net.http_GET(f_url, headers=headers).content
        f_url = re.search(r'''data-url\s*=\s*('|")(?P<link>(?:(?!\1).)+)''', r)
        if f_url:
            r = self.net.http_GET(f_url.group('link') + "=mm,hls-vm-vf,dr.sdr,sdrCodec.vp9.h264?cpn=%s&alr=true" % self._get_random_cpn(), headers=headers)
            url = r.get_headers(as_dict=True).get('Content-Location')
            headers.update({"Origin": "https://youtube.googleapis.com"})
            return url + helpers.append_headers(headers)

        ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    def _get_random_cpn(self):
        # nonce, not necessarily needed
        return ''.join(choice(ascii_letters + digits) for _ in range(16))
