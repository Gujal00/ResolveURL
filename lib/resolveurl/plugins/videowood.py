"""
    Plugin for ResolveUrl
    Copyright (C) 2015 tknorris

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
from resolveurl.plugins.lib import aadecode
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VideowoodResolver(ResolveUrl):
    name = "videowood"
    domains = ['videowood.tv']
    pattern = r'(?://|\.)(videowood\.tv)/(?:embed/|video/)([0-9a-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        try:
            html = html.encode('utf-8')
        except:
            pass
        if "This video doesn't exist." in html:
            raise ResolverError('The requested video was not found.')

        match = re.search(r"split\('\|'\)\)\)\s*(.*?)</script>", html)
        if match:
            aa_text = aadecode.decode(match.group(1))
            match = re.search("'([^']+)", aa_text)
            if match:
                stream_url = match.group(1)
                return stream_url + helpers.append_headers({'User-Agent': common.FF_USER_AGENT})

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/embed/{media_id}')
