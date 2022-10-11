"""
    Plugin for ResolveURL
    Copyright (C) 2011 t0mm0

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
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VimeoResolver(ResolveUrl):
    name = 'Vimeo'
    domains = ['vimeo.com', 'player.vimeo.com']
    pattern = r'(?://|\.)(vimeo\.com)/(?:video/)?([^\n]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.FF_USER_AGENT}
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
            headers.update({'Referer': referer})
        else:
            media_id = media_id.split('/')[0]
            media_id = media_id.split('?')[0]
            referer = False

        web_url = self.get_url(host, media_id)
        if not referer:
            headers.update({'Referer': 'https://vimeo.com/',
                            'Origin': 'https://vimeo.com'})

        html = self.net.http_GET(web_url, headers).content
        data = json.loads(html)
        sources = [(vid['height'], vid['url']) for vid in data.get('request', {}).get('files', {}).get('progressive', {})]
        if sources:
            sources.sort(key=lambda x: x[0], reverse=True)
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://player.vimeo.com/video/{media_id}/config')
