"""
    Plugin for ResolveURL
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
import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamCommunityResolver(ResolveUrl):
    name = 'StreamCommunity'
    domains = ['streamingcommunity.xyz', 'streamingcommunity.one', 'streamingcommunity.vip',
               'streamingcommunity.work', 'streamingcommunity.name', 'streamingcommunity.video',
               'streamingcommunity.live', 'streamingcommunity.tv', 'streamingcommunity.space',
               'streamingcommunity.art', 'streamingcommunity.fun', 'streamingcommunity.website',
               'streamingcommunity.host', 'streamingcommunity.site', 'streamingcommunity.bond',
               'streamingCommunity.icu', 'streamingcommunity.bar', 'streamingcommunity.top',
               'streamingcommunity.cc', 'streamingcommunity.monster', 'streamingcommunity.press',
               'streamingcommunity.business', 'streamingcommunity.org', 'streamingcommunity.best',
               'streamingcommunity.agency', 'streamingcommunity.blog', 'streamingcommunity.tech',
               'streamingcommunity.golf', 'streamingcommunity.city', 'streamingcommunity.help',
               'streamingcommunity.blue', 'streamingcommunity.codes', 'streamingcommunity.bet']
    pattern = r'(?://|\.)(streamingcommunity\.' \
        r'(?:one|xyz|video|vip|work|name|live|tv|space|art|fun|website|host|site|bond|icu|bar|top|' \
        r'cc|monster|press|business|org|best|agency|blog|tech|golf|city|help|blue|codes|bet))' \
        r'/watch/(\d+(?:\?e=)?\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'''scws_id&quot;:(\d+)''', html)
        if match:
            scws_id = match.group(1)
            headers.update({'Referer': web_url})
            html = self.net.http_GET('https://scws.work/videos/' + scws_id, headers=headers).content
            a = json.loads(html).get('client_ip')
            url = 'https://scws.work/master/{0}?{1}'.format(scws_id, self.get_token(a))
            return url + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://streamingcommunity.bet/watch/{media_id}')

    def get_token(self, a):
        import time
        from hashlib import md5
        t = int(time.time() + 172800)
        s = '{0}{1} Yc8U6r8KjAKAepEA'.format(t, a)
        c = helpers.b64encode(md5(s.encode('utf-8')).digest())
        c = c.replace('=', '').replace('+', '-').replace('/', '_')
        return 'token={0}&expires={1}&n=1'.format(c, t)
