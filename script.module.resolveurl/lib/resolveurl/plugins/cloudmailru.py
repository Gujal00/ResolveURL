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
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib import helpers


class CloudMailRuResolver(ResolveUrl):
    name = 'CloudMailRu'
    domains = ['cloud.mail.ru']
    pattern = r'(?://|\.)(cloud\.mail\.ru)/public/([0-9A-Za-z]+/[^/]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://mail.ru/'}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'"weblink_get".+?url":\s*"([^"]+)', html, re.DOTALL)
        if r:
            strurl = '{0}/{1}'.format(r.group(1), media_id)
            tok = re.search(r'"tokens"[^}]+"download"\s*:\s*"([^"]+)', html, re.DOTALL)
            if tok:
                strurl += '?key={0}'.format(tok.group(1))
            return strurl + helpers.append_headers(headers)
        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/public/{media_id}')
