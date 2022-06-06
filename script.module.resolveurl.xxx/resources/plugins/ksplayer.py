"""
    Plugin for ResolveURL
    Copyright (C) 2018 Whitecream

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

from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import re


class KSplayerResolver(ResolveUrl):
    name = 'ksplayer'
    domains = ['ksplayer.com']
    pattern = r'(?://|\.)(ksplayer\.com)/(?:plugins/mediaplayer/site/_embed\.php\?u=|player/|embed/)([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': web_url}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        sources = []
        for r in re.finditer(r'''href=["']?(?P<url>[^"']+)["']?>DOWNLOAD\s*<span>(?P<label>[^<]+)''', html, re.DOTALL):
            match = r.groupdict()
            stream_url = match['url'].replace('&amp;', '&')
            label = match.get('label', '0')
            sources.append([label, stream_url])
        if len(sources) > 1:
            sources.sort(key=lambda x: int(re.sub(r"\D", "", x[0])), reverse=True)
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://stream.{host}/download/{media_id}/')

    @classmethod
    def _is_enabled(cls):
        return True
