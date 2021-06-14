"""
    plugin for ResolveURL
    Copyright (C) 2021 gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamCommunityResolver(ResolveUrl):
    name = "streamcommunity"
    domains = ['streamingcommunity.xyz', 'streamingcommunity.one']
    pattern = r'(?://|\.)(streamingcommunity\.(?:one|xyz))/watch/(\d+(?:\?e=)?\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'''<video-player.+?video_url.+?(http[^&]+)''', html, re.DOTALL)
        if match:
            url = match.group(1).replace('\\', '')
            headers.update({'Referer': web_url})
            a = self.net.http_GET('https://streamingcommunity.xyz/client-address', headers=headers).content
            return url + self.get_token(a) + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://streamingcommunity.xyz/watch/{media_id}')

    def get_token(self, a):
        import time
        import base64
        from Cryptodome.Hash import MD5
        t = int(time.time() + 172800)
        s = '{0}{1} Yc8U6r8KjAKAepEA'.format(t, a)
        c = base64.b64encode(MD5.new(s.encode('utf-8')).digest()).decode('utf-8')
        c = c.replace('=', '').replace('+', '-').replace('/', '_')
        return '?token={0}&expires={1}'.format(c, t)
