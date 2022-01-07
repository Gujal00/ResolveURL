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

import json
import re
from six.moves import urllib_parse
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class FastdriveResolver(ResolveUrl):
    name = "fastdrive"
    domains = ['fastdrive.io']
    pattern = r'(?://|\.)(fastdrive\.io)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        rurl = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r"btn--primary'\s*href='([^']+)", html)
        if r:
            common.kodi.sleep(7000)
            g = self.net.http_GET(r.group(1), headers=headers)
            ghtml = g.content
            gurl = g.get_url()
            data = helpers.get_hidden(ghtml)
            headers.update({
                'Origin': urllib_parse.urljoin(gurl, '/')[:-1],
                'Referer': gurl,
                'X-Requested-With': 'XMLHttpRequest'
            })
            purl = re.findall('<form.+?action="([^"]+)', ghtml)[0]
            if purl.startswith('/'):
                purl = urllib_parse.urljoin(gurl, purl)
            common.kodi.sleep(5000)
            html = self.net.http_POST(purl, form_data=data, headers=headers).content
            jd = json.loads(html)
            if jd.get('status') == "success":
                headers.pop('X-Requested-With')
                return jd.get('url') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
