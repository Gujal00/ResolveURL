"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de, gujal

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class UploadEverResolver(ResolveUrl):
    name = 'UploadEver'
    domains = ['uploadever.com', 'uploadever.in']
    pattern = r'(?://|\.)(uploadever\.(?:com|in))/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        r = self.net.http_GET(web_url, headers=headers)
        if web_url != r.get_url():
            web_url = r.get_url()
        html = r.content
        rurl = urllib_parse.urljoin(web_url, '/')
        token = helpers.girc(html, rurl)
        headers.update({
            'Origin': rurl[:-1],
            'Referer': web_url
        })
        payload = helpers.get_hidden(html)
        payload.update({
            'referer': '',
            'method_free': '',
            'method_premium': '',
            'adblock_detected': 0,
            'g-recaptcha-response': token
        })
        common.kodi.sleep(10000)
        html = self.net.http_POST(web_url, form_data=payload, headers=headers).content
        url = re.search(r'btn\s*btn-dow\s*(?:recaptchav2)?"\s*href="(http[^"]+)', html)
        if url:
            path = urllib_parse.urlparse(url.group(1)).path[1:]
            try:
                url = helpers.b64decode(path)
            except Exception:
                url = url.group(1)
            return url.replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://uploadever.in/{media_id}')
