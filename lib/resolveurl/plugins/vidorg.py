"""
Plugin for ResolveURL
Copyright (c) 2018 gujal

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


class VidorgResolver(ResolveUrl):
    name = 'vidorg.net'
    domains = ["vidorg.net", "vidpiz.xyz"]
    pattern = r'(?://|\.)(vid(?:org|piz)\.(?:net|xyz))/(?:embed[/-])?([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.scrape_sources(html,
                                         patterns=[r'''file:"(?P<url>[^"]+)",label:"(?P<label>[^"]+)'''],
                                         generic_patterns=False)
        if sources:
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/embed-{media_id}.html')
