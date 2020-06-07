# -*- coding: UTF-8 -*-
"""
    Plugin fore ResolveURL
    Copyright (C) 2020  gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class SaruchResolver(ResolveUrl):
    name = "saruch"
    domains = ["saruch.co"]
    pattern = r'(?://|\.)(saruch\.co)/(?:embed|video)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://{0}/videos/{1}'.format(host, media_id),
                   'X-Requested-With': 'XMLHttpRequest'}
        js_data = json.loads(self.net.http_GET(web_url, headers=headers).content)

        if js_data.get('video').get('sources'):
            sources = []
            for item in js_data.get('video').get('sources'):
                sources.append((item.get('label'), item.get('file')))
            source = helpers.pick_source(helpers.sort_sources_list(sources))
            headers.pop('X-Requested-With')
            headers.update({"Range": "bytes=0-"})
            de = js_data.get('de')
            en = js_data.get('en')
            return '{0}?de={1}&en={2}{3}'.format(source, de, en, helpers.append_headers(headers))

        raise ResolverError('Stream not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://api.saruch.co/videos/{media_id}/stream?referrer=https:%2F%2F{host}%2Fvideo%2F{media_id}')
