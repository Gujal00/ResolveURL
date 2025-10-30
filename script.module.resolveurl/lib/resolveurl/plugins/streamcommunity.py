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
from six.moves import urllib_parse
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
               'streamingcommunity.icu', 'streamingcommunity.bar', 'streamingcommunity.top',
               'streamingcommunity.cc', 'streamingcommunity.monster', 'streamingcommunity.press',
               'streamingcommunity.business', 'streamingcommunity.org', 'streamingcommunity.best',
               'streamingcommunity.agency', 'streamingcommunity.blog', 'streamingcommunity.tech',
               'streamingcommunity.golf', 'streamingcommunity.city', 'streamingcommunity.help',
               'streamingcommunity.blue', 'streamingcommunity.codes', 'streamingcommunity.bet',
               'streamingcommunity.photos', 'streamingcommunityz.li', 'streamingcommunityz.bz',
               'streamingcommunityz.tv', 'streamingcommunityz.lu', 'streamingcommunityz.ch']
    pattern = r'(?://|\.)(streamingcommunityz?\.' \
        r'(?:one|xyz|video|vip|work|name|live|tv|space|art|fun|website|host|site|bond|icu|bar|top|' \
        r'cc|monster|press|business|org|best|agency|blog|tech|golf|city|help|blue|codes|bet|li|bz|' \
        r'photos|lu|ch))' \
        r'/(?:[a-z]{2}/)?watch/(\d+(?:\?e=)?\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'''<iframe.+?src="([^"]+)''', html, re.DOTALL)
        if match:
            vix = match.group(1).replace('&amp;', '&')
            headers.update({'Referer': web_url})
            html = self.net.http_GET(vix, headers=headers).content
            params = re.search(r'''window\.masterPlaylist\s*=\s*([^<]+)''', html)
            if params:
                params = params.group(1)
                surl = re.search(r"url:\s*'([^']+)", params)
                tok = re.search(r"token':\s*'([^']+)", params)
                exp = re.search(r"expires':\s*'([^']+)", params)
                if surl and tok and exp:
                    headers.update({'Referer': urllib_parse.urljoin(vix, '/')})
                    url = '{0}?token={1}&expires={2}&h=1'.format(surl.group(1), tok.group(1), exp.group(1))
                    return url + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        if '?e=' in media_id:
            media_id = media_id.replace('?e=', '?episode_id=')
        return self._default_get_url(host, media_id, template='https://{host}/it/iframe/{media_id}')
