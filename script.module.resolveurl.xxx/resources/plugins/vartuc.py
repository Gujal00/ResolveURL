"""
    Plugin for ResolveURL
    Copyright (C) 2018 holisticdioxide

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


class VartucResolver(ResolveUrl):
    name = 'vartuc'
    domains = ['vartuc.com', 'azblowjobtube.com']
    pattern = r'(?://|\.)(vartuc\.com|azblowjobtube\.com)/embed/([^"]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content
        js_link = re.compile("src='(/kt_player/.*?)'", re.DOTALL | re.IGNORECASE).search(html).group(1)
        js_path = 'https://{0}{1}'.format(host, js_link)
        js = self.net.http_GET(js_path, headers=headers).content
        gvars = re.findall(r'(g\w{4}=".")', js)
        vurl = re.search(r'video_url:([^,]+)', js)
        if vurl:
            for gvar in gvars:
                exec(gvar)
            return eval(vurl.group(1)) + helpers.append_headers(headers)
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
