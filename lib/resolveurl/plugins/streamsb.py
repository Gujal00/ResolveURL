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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamSBResolver(ResolveUrl):
    name = "streamsb"
    domains = ["sbembed.com", "sbembed1.com", "sbplay.org", "sbvideo.net", "streamsb.net", "sbplay.one",
               "cloudemb.com", "playersb.com", "tubesb.com", "sbplay1.com", "embedsb.com", "watchsb.com"]
    pattern = r'(?://|\.)((?:watch|embed|tube|player|cloudemb|stream)?s?b?(?:embed\d?|play\d?|video)?\.' \
              r'(?:com|net|org|one))/(?:embed-|e/|play/|d/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = re.findall(r'download_video([^"]+)[^\d]+\d+x(\d+)', html)
        if sources:
            sources.sort(key=lambda x: int(x[1]), reverse=True)
            sources = [(x[1] + 'p', x[0]) for x in sources]
            code, mode, hash = eval(helpers.pick_source(sources))
            dl_url = 'https://{0}/dl?op=download_orig&id={1}&mode={2}&hash={3}'.format(host, code, mode, hash)
            html = self.net.http_GET(dl_url, headers=headers).content
            r = re.search('href="([^"]+)">Direct', html)
            if r:
                return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/d/{media_id}.html')
