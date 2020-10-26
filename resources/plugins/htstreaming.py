"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class HTStreamingResolver(ResolveUrl):
    name = 'htstreaming'
    domains = ['htstreaming.com']
    pattern = r'(?://|\.)(htstreaming\.com)/player/index\.php\?data=([0-9a-f]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.RAND_UA}
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        vurl, svr = re.findall('videoUrl":"([^"]+)","videoServer":"([^"]+)', html)[0]
        headers.update({'Referer': web_url,
                        'Accept': '*/*'})
        eurl = 'https://{0}{1}?s={2}&d='.format(host, vurl.replace('\\', ''), svr)
        ehtml = self.net.http_GET(eurl, headers=headers).content
        sources = re.findall(r'Resolution=\d+x(\d+)\n([^\n]+)', ehtml, re.IGNORECASE)
        if sources:
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
