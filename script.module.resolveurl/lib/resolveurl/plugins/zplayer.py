"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal
    Copyright (C) 2020 groggyegg

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
from six.moves import urllib_parse
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class ZPlayerResolver(ResolveUrl):
    name = "zplayer"
    domains = ["zplayer.live"]
    pattern = r'(?://|\.)(zplayer\.live)/(?:embed/|video/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers=headers).content
        d = re.search(r"download_video\('([^']+)','([^']+)','([^']+)", html)
        if d:
            dl_url = urllib_parse.urljoin(web_url, '/dl?op=download_orig&id={0}&mode={1}&hash={2}'.format(d.group(1), d.group(2), d.group(3)))
            html = self.net.http_GET(dl_url, headers=headers).content
            r = re.search('href="([^"]+)"[^>]+>(?:Direct|Enlace)', html)
            if r:
                return r.group(1) + helpers.append_headers(headers)

        eurl = web_url.replace('/video/', '/embed/')
        html = self.net.http_GET(eurl, headers=headers).content
        sources = helpers.scrape_sources(html, patterns=[r'''sources:\s*[[{]+\s*file:\s*"(?P<url>[^"]+)'''], generic_patterns=False)
        if sources:
            return helpers.pick_source(sorted(sources, reverse=True)) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://v2.{host}/video/{media_id}')
