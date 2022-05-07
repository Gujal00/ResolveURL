"""
    Plugin for ResolveUrl
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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class AparatResolver(ResolveUrl):
    name = "Aparat"
    domains = ['aparat.cam', 'wolfstream.tv']
    pattern = r'(?://|\.)((?:aparat\.cam|wolfstream\.tv))/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net(ssl_verify=False)

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        headers.update({'Referer': web_url})

        match = re.search(r'Video is processing now\.', html)
        if match:
            raise ResolverError('Video is still processing. Try later')

        match = re.search(r'&hash=([^&]+)', html)
        if match:
            web_url = 'https://wolfstream.tv/dl?op=download_orig&id={0}&mode=o&hash={1}'.format(media_id, match.group(1))
            html2 = self.net.http_GET(web_url, headers=headers).content
            r = re.search(r'<a\s*href="([^"]+)[^>]+>Direct', html2)
            if r:
                headers.update({'verifypeer': 'false'})
                return r.group(1) + helpers.append_headers(headers)

        match = re.search(r'(?:src|file):\s*"([^"]+)', html)
        if match:
            html2 = self.net.http_GET(match.group(1), headers=headers).content
            sources = re.findall(r'RESOLUTION=\d+x(?P<label>[\d]+).+\n(?!#)(?P<url>[^\n]+)', html2, re.IGNORECASE)
            if sources:
                headers.update({'verifypeer': 'false'})
                return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://wolfstream.tv/embed-{media_id}.html')
