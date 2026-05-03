"""
    Plugin for ResolveURL
    Copyright (c) 2026 gujal

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class AnonMP4Resolver(ResolveUrl):
    name = 'AnonMP4'
    domains = ['anonmp4.help']
    pattern = r'(?://|\.)(anonmp4\.help)/embed/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        a = re.search(r"SINGLE_API_URL\s*=\s*'([^']+)", html)
        if a:
            ref = urllib_parse.urljoin(web_url, '/')
            headers.update({'Referer': ref, 'Origin': ref[:-1]})
            html = self.net.http_GET(a.group(1), headers=headers).content
            r = json.loads(html)
            if 'hls' in r.keys():
                url = r.get('hls') + helpers.append_headers(headers)
                if subs:
                    subtitles = {}
                    s = r.get('subtitles')
                    if s:
                        subtitles = {x.get('language'): x.get('url') for x in s}
                    return url, subtitles
                return url
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
