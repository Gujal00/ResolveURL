"""
    Plugin for ResolveURL
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
import base64
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class TrollVidResolver(ResolveUrl):
    name = 'trollvid.net'
    domains = ['trollvid.net', 'trollvid.io', 'mp4edge.com']
    pattern = r'(?://|\.)(trollvid(?:\.net|\.io)|mp4edge\.com)/(?:embed\.php.file=|embed/|stream/)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        stream_url = None
        try:
            stream_url = re.search(r'url\s*:\s*"(http.+?)"', html).group(1)
        except:
            pass

        if not stream_url:
            try:
                stream_url = re.search(r'unescape\(\'(http.+?)\'', html).group(1)
            except:
                pass

        if not stream_url:
            try:
                stream_url = base64.b64decode(re.search(r'atob\(\'(.+?)\'', html).group(1))
            except:
                pass

        if not stream_url:
            raise ResolverError('File not found')

        return urllib_parse.unquote_plus(stream_url) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://trollvid.net/embed/%s' % media_id
