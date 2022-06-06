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
import json
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class HTStreamingResolver(ResolveUrl):
    name = 'htstreaming'
    domains = ['htstreaming.com']
    pattern = r'(?://|\.)(htstreaming\.com)/(?:player|video)/(?:index\.php\?data=)?([0-9a-f]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        eurl = self.get_url2(host, media_id)
        headers.update({
            'Referer': web_url,
            'Origin': urllib_parse.urljoin(web_url, '/')[:-1],
            'X-Requested-With': 'XMLHttpRequest'
        })
        html = self.net.http_POST(eurl, form_data="hash={0}".format(media_id), headers=headers).content
        vurl = json.loads(html).get('videoSource')
        if vurl:
            headers.pop('Origin')
            headers.pop('X-Requested-With')
            headers.update({'Accept': '*/*'})
            ehtml = self.net.http_GET(vurl, headers=headers).content
            sources = re.findall(r'Resolution=\d+x(\d+).+\n([^\n]+)', ehtml, re.IGNORECASE)
            if sources:
                cookies = self.net.get_cookies(True)
                headers.update({'Cookie': 'fireplayer={0}'.format(cookies.get('fireplayer'))})
                return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/video/{media_id}')

    def get_url2(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}&do=getVideo')

    @classmethod
    def _is_enabled(cls):
        return True
