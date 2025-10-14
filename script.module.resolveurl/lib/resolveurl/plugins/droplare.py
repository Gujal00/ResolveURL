"""
    Plugin for ResolveURL
    Copyright (C) 2026 gujal

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

from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class DroplareResolver(ResolveUrl):
    name = 'Droplare'
    domains = ['droplare.cc', 'droplare.ws', 'droplaress.cc']
    pattern = r'(?://|\.)(droplares*\.(?:cc|ws))/([0-9a-zA-Z$:/.-_]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False

        web_url = self.get_url(host, media_id)
        if not referer:
            referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        done = False
        cookies = []
        uri = web_url
        while not done:
            if cookies:
                headers.update({'Cookie': '; '.join(cookies)})
            r = self.net.http_GET(uri, headers=headers, redirect=False)
            hdrs = r.get_headers(as_dict=True)
            cookie = hdrs.get('Set-Cookie')
            if cookie:
                cookie = cookie.split(';')[0]
                cookies.append(cookie)
            location = hdrs.get('Location')
            if location:
                uri = location
            else:
                html = r.content
                done = True

        data = helpers.get_hidden(html)
        src = helpers.get_redirect_url(web_url, form_data=data, headers=headers)
        if src != web_url:
            headers.update({
                'Referer': 'https://{0}/'.format(host),
                'verifypeer': 'false'
            })
            return src + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
