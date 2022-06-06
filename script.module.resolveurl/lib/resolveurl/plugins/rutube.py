"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class RuTubeResolver(ResolveUrl):
    name = 'RuTube'
    domains = ['rutube.ru']
    pattern = r'(?://|\.)(rutube\.ru)/(?:play/embed/|video/)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.FF_USER_AGENT}
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        html = json.loads(html)
        url = ''
        json_data = html.get('video_balancer')
        if json_data:
            url = json_data.get('m3u8')
            if not url:
                json_url = json_data.get('json')
                html = self.net.http_GET(json_url, headers=headers).content
                js_data = json.loads(html)
                if js_data.get('results', False):
                    return js_data.get('results')[0] + helpers.append_headers(headers)

        if not url:
            json_data = html.get('live_streams')
            if json_data:
                url = json_data.get('hls')[0].get('url')

        if url:
            headers.update({'Origin': 'http://rutube.ru'})
            mbtext = self.net.http_GET(url, headers=headers).content
            sources = re.findall(r'RESOLUTION=\d+x(?P<label>\d+).*\n(?P<url>[^?\n]+)', mbtext, re.IGNORECASE)
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/api/play/options/{media_id}/?format=json&no_404=true')
