"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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
import six
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VipTubeResolver(ResolveUrl):
    name = 'VipTube'
    domains = ['viptube.com', 'proporn.com', 'vivatube.com', 'winporn.com']
    pattern = r'(?://|\.)((?:viptube|proporn|vivatube|winporn)\.com)/(?:\w\w/)?(?:video|embed)/([a-zA-Z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://www.{0}/'.format(host)}
        resp = self.net.http_GET(web_url, headers=headers).content
        jdata = json.loads(resp).get('files')
        if jdata:
            sources = []
            for k, v in six.iteritems(jdata):
                qual = {'lq': '360p', 'hq': '720p', '4k': '2160p'}.get(k)
                if v:
                    sources.append((qual, v))

        if sources:
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/player_config_json/?vid={media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
