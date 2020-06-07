"""
Plugin for ResolveUrl
Copyright (C) 2020 gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidCloud9Resolver(ResolveUrl):
    name = "vidcloud9.com"
    domains = ['vidcloud9.com']
    pattern = r'(?://|\.)(vidcloud9\.com)/streaming.php\?id=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://{0}/'.format(host),
                   'X-Requested-With': 'XMLHttpRequest'}
        js_data = json.loads(self.net.http_GET(web_url, headers=headers).content)
        sources = js_data.get('source', None)
        if sources:
            sources = [(source.get('label'), source.get('file')) for source in sources]
            headers.pop('X-Requested-With')
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/ajax.php?id={media_id}')
