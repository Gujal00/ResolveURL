"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal

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
import re
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidNeoResolver(ResolveUrl):
    name = 'VidNeo'
    domains = ['vidneo.cc']
    pattern = r'(?://|\.)(vidneo\.cc)/e/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'({\\"src.+})]}]', html)
        if r:
            jd = json.loads(r.group(1).replace('\\', ''))
            src = jd.get('src')
            if src:
                if src.startswith('/'):
                    src = urllib_parse.urljoin(web_url, src)
                headers.update({'Referer': web_url})
                src += helpers.append_headers(headers)
                if subs:
                    subtitles = {}
                    s = jd.get('subtitleTracks')
                    if s:
                        subtitles = {x.get('label'): urllib_parse.urljoin(web_url, '/api' + x.get('vttPath')) for x in s}
                    return src, subtitles
                return src
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')
