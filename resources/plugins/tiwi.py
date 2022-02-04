"""
    Plugin for ResolveURL
    Copyright (C) 2018 Whitecream

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


This plugin returns a MPEG Dash file (.mpd)
To play this with Kodi you'll need to at the following properties to ListItem:
listitem.setProperty('inputstreamaddon','inputstream.adaptive')
listitem.setProperty('inputstream.adaptive.manifest_type','mpd')

Also, inputstream.adaptive needs to be installed and enabled.
"""

import re
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class TiwiResolver(ResolveUrl):
    name = 'tiwi'
    domains = ['tiwi.kiwi']
    pattern = r'(?://|\.)(tiwi\.kiwi)/(?:embed[/-])?([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.RAND_UA}
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        source = re.search(r'''<source\s*src="([^'"]+)"''', html, re.DOTALL)
        if source:
            return source.group(1) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')

    @classmethod
    def _is_enabled(cls):
        return True
