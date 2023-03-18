"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de

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


class StreamEmbedResolver(ResolveUrl):
    name = 'StreamEmbed'
    domains = ['bullstream.xyz', 'mp4player.site']
    pattern = r'(?://|\.)((?:bullstream|mp4player)\.(?:xyz|site))/watch\?v=([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        data = re.search(r'sniff\("\w+","(\d+)","(\w+)"', html)
        if data:
            headers.update({'Accept': '*/*', 'Referer': web_url})
            url = 'https://{}/m3u8/{}/{}/master.txt?s=1&cache=1'.format(
                host, data.group(1), data.group(2)
            )
            html = self.net.http_GET(url, headers=headers).content
            if 'type=audio' not in html.lower():
                sources = re.findall(r'\d+x(?P<label>[\d]+).*\n(?P<url>[^\n]+)', html)
                if sources:
                    return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)
            else:
                return url + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/watch?v={media_id}')
