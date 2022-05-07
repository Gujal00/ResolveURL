"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal, Anis3

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

import re
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class UpStreamResolver(ResolveUrl):
    name = "UpStream"
    domains = ['upstream.to']
    pattern = r'(?://|\.)(upstream\.to)/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        headers.update({'Referer': web_url})

        if 'sorry' in html:
            raise ResolverError("Video Deleted")

        r = re.search(r"redirect_vid\('([^']+)','([^']+)','([^']+)'", html)
        if r:
            surl = 'https://{0}/dl?op=download_orig&id={1}&mode={2}&hash={3}'.format(
                host, r.group(1), r.group(2), r.group(3)
            )
            dhtml = self.net.http_GET(surl, headers=headers).content
            s = re.search('href="([^"]+)">Direct', dhtml)
            if s:
                return s.group(1) + helpers.append_headers(headers)

        html += helpers.get_packed_data(html)
        sources = helpers.scrape_sources(
            html,
            patterns=[r'''sources:\s*\[(?:{file:)?\s*"(?P<url>[^"]+)'''],
            generic_patterns=False
        )
        if sources:
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError("Video not found")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
