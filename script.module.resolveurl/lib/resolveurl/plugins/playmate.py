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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class PlaymateResolver(ResolveUrl):
    name = 'Playmate'
    domains = ['playmate.to']
    pattern = r'(?://|\.)(playmate\.to)/(?:watch|embed|e|v)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': urllib_parse.urljoin(web_url, '/')}
        pdata = {'c': media_id,
                 'd': 'web'}
        html = self.net.http_POST(web_url, form_data=pdata, headers=headers, jdata=True).content
        r = json.loads(html)
        if r.get('sx'):
            url = r.get('sx') + helpers.append_headers(headers)
            if subs:
                subtitles = {}
                s = r.get('kx')
                if s:
                    subtitles = {x.get('sl'): x.get('sf') for x in s}
                return url, subtitles
            return url

        raise ResolverError('Unable to locate stream URL.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/api/s')
