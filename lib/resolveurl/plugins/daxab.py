"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal

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
import json
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common


class DaxabResolver(ResolveUrl):
    name = "daxab"
    domains = ["daxab.com"]
    pattern = r'(?://|\.)(daxab\.com)/player/([^\n]+)'

    def get_media_url(self, host, media_id):
        if '|' in media_id:
            media_id, referer = media_id.split('|')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        if not referer:
            referer = web_url
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        params = re.search(r'video:\s*([^;]+)', html)
        if params:
            params = params.group(1)
            id = re.findall(r'cdn_id:\s*"([^"]+)', params)[0]
            id1, id2 = id.split('_')
            server = re.findall(r'server:\s*"([^"]+)', params)[0][::-1]
            server = base64.b64decode(server.encode('ascii')).decode('ascii')
            sources = json.loads(re.findall(r'cdn_files:\s*([^}]+})', params)[0])
            sources = [(key[4:], 'https://{0}/videos/{1}/{2}/{3}'.format(server, id1, id2, sources[key].replace('.', '.mp4?extra=')))
                       for key in list(sources.keys())]
            return helpers.pick_source(sorted(sources, reverse=True)) + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/{media_id}')
