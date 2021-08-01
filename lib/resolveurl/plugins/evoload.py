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

import re, json
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class EvoLoadResolver(ResolveUrl):
    name = "evoload"
    domains = ["evoload.io"]
    pattern = r'(?://|\.)(evoload\.io)/(?:e|f|v)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        surl = 'https://evoload.io/SecurePlayer'
        web_url = self.get_url(host, media_id)
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers).content
        passe = re.search('<div id="captcha_pass" value="(.+?)"></div>', html).group(1)
        headers.update({'Origin': rurl[:-1]})
        crsv = self.net.http_GET('https://csrv.evosrv.com/captcha?m412548', headers).content
        post = {"code": media_id, "csrv_token": crsv, "pass": passe, "token": "ok"}
        shtml = self.net.http_POST(surl, form_data=post, headers=headers, jdata=True).content
        r = json.loads(shtml).get('stream')
        if r:
            surl = r.get('backup') if r.get('backup') else r.get('src')
            if surl:
                return surl + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
