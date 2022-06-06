"""
    Plugin for ResolveURL
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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VideaResolver(ResolveUrl):
    name = 'Videa'
    domains = ['videa.hu', 'videakid.hu']
    pattern = r'(?://|\.)((?:videa|videakid)\.hu)/(?:player/?\?v=|player/v/|videok/)(?:.*-|)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://{0}/player?v={1}'.format(host, media_id),
                   'X-Requested-With': 'XMLHttpRequest'}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = re.findall(r'video_source\s*name="(?P<label>[^"]+)[^>]+>(?P<url>[^<]+)', html)

        if sources:
            source = helpers.pick_source(helpers.sort_sources_list(sources))
            source = 'https:' + source if source.startswith('//') else source
            headers.pop('X-Requested-With')
            headers.update({'Origin': 'https://{}'.format(host)})
            return source.replace('&amp;', '&') + helpers.append_headers(headers)

        raise ResolverError('Stream not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/videaplayer_get_xml.php?v={media_id}&start=0&referrer=http://{host}')
