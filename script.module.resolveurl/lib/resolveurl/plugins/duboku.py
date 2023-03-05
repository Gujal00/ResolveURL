"""
    Plugin for ResolveURL
    Copyright (C) 2023 groggyegg

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
from resolveurl.resolver import ResolverError, ResolveUrl


class DubokuResolver(ResolveUrl):
    name = 'Duboku'
    domains = ['duboku.ru', 'duboku.tv', 'duboku.fun', 'duboku.com']
    pattern = r'(?://|\.)(duboku\.(?:ru|tv|fun|com))/((?:video|vodplay)/\d+-\d+-\d+\.html)'

    def get_media_url(self, host, media_id):
        if host.endswith(('.fun', '.com')):
            host = 'duboku.tv'
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'var\s*player_[a-z]{0,4}\s*=\s*([^<]+)', html)

        if match:
            pd = json.loads(match.group(1))
            url = pd.get('url')
            url_next = pd.get('url_next')
            encrypt = pd.get('encrypt')
            if encrypt == 1:
                url = urllib_parse.unquote(url)
                url_next = urllib_parse.unquote(url_next)
            elif encrypt == 2:
                url = urllib_parse.unquote(helpers.duboku_decode(url))
                url_next = urllib_parse.unquote(helpers.duboku_decode(url_next))

            if url.startswith('http'):
                return url + helpers.append_headers(headers)
            else:
                return url_next + helpers.append_headers(headers)

        raise ResolverError('Unable to locate Video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
