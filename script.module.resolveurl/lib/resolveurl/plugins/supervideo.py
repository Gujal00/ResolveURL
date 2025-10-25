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


class SuperVideoResolver(ResolveUrl):
    name = 'SuperVideo'
    domains = ['supervideo.tv', 'supervideo.cc']
    pattern = r'(?://|\.)(supervideo\.(?:tv|cc))/(?:embed-|e/|k/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.IOS_USER_AGENT,
                   'Referer': 'https://{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content

        pdata = helpers.get_packed_data(html)
        if pdata:
            sources = helpers.scrape_sources(
                pdata,
                patterns=[r'''{\s*file:\s*"(?P<url>[^"]+)"\s*}'''],
                generic_patterns=False
            )
            if sources:
                return helpers.pick_source(sources) + helpers.append_headers(headers)

        source = re.search(r"download_video.+?'([^']+)','([^']+)'\)", html)
        if source:
            dl_url = 'https://{0}/dl?op=download_orig&id={1}&mode={2}&hash={3}'.format(host, media_id, source.group(1), source.group(2))
            html = self.net.http_GET(dl_url, headers=headers).content
            r = re.search(r'btn_direct-download"\s*href="([^"]+)', html)
            if r:
                return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
