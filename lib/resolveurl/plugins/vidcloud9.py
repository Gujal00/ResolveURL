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

from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidCloud9Resolver(ResolveUrl):
    name = "vidcloud9.com"
    domains = ['vidcloud9.com', 'vidnode.net', 'vidnext.net', 'vidembed.net', 'vidembed.cc']
    pattern = r'(?://|\.)((?:vidcloud9|vidnode|vidnext|vidembed)\.(?:com|net|cc))/(?:streaming|load(?:server)?)\.php\?id=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://vidembed.cc/'}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.scrape_sources(html)
        if sources:
            headers.update({'Origin': 'https://vidembed.cc'})
            return helpers.pick_source(sources) + helpers.append_headers(headers)
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidembed.cc/loadserver.php?id={media_id}')
