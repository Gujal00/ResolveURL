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
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search("href='([^']+).+?GET LINK", html)
        if r:
            g = self.net.http_GET(r.group(1), headers=headers)
            html = g.content
            gp = urllib_parse.urlparse(g.get_url())
            data = helpers.get_hidden(html)
            headers.update({
                'Origin': '{0}://{1}'.format(gp.scheme, gp.netloc),
                'Referer': g.get_url(),
                'X-Requested-With': 'XMLHttpRequest'
            })
            purl = re.findall('<form.+?action="([^"]+)', html)[0]
            if purl.startswith('/'):
                purl = '{0}://{1}{2}'.format(gp.scheme, gp.netloc, purl)
            common.kodi.sleep(5000)
            html = self.net.http_POST(purl, form_data=data, headers=headers).content
            jd = json.loads(html)
            if jd.get('status') == "success":
                headers.pop('X-Requested-With')
                return jd.get('url') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
