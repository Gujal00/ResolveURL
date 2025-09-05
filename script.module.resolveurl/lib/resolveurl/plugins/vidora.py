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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VidoraResolver(ResolveUrl):
    name = 'Vidora'
    domains = ['vidora.stream']
    pattern = r'(?://|\.)(vidora\.stream)/(?:embed/|embed-)?([0-9a-zA-Z=]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        html += helpers.get_packed_data(html)
        r = re.search(r'Playerjs\([^)]+?file:\s*"([^"]+)', html, re.DOTALL)
        if r:
            headers.update({
                'Origin': 'https://{0}'.format(host),
                'Referer': 'https://{0}/'.format(host)
            })
            surl = r.group(1) + helpers.append_headers(headers)
            if subs:
                subtitles = {}
                s = re.search(r'Playerjs\([^)]+?subtitle":\s*"([^"]+)', html, re.DOTALL)
                if s:
                    subs = s.group(1).split(',')
                    for sub in subs:
                        lang, vtt = sub.split(']')
                        subtitles.update({lang[1:]: vtt})
                return surl, subtitles
            return surl
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
