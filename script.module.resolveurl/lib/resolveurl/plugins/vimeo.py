"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VimeoResolver(ResolveUrl):
    name = 'Vimeo'
    domains = ['vimeo.com', 'player.vimeo.com']
    pattern = r'(?://|\.)(vimeo\.com)/(?:video/)?([0-9a-zA-Z.:/$&?=]+)'

    def get_media_url(self, host, media_id, subs=False):
        headers = {'User-Agent': common.FF_USER_AGENT}
        ref = 'https://vimeo.com/'
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
            headers.update({'Referer': referer})
        else:
            media_id = media_id.split('?')[0]
            media_id = media_id.split('/')[0]
            referer = False

        web_url = self.get_url(host, media_id)
        if not referer:
            headers.update({'Referer': ref,
                            'Origin': ref[:-1]})

        html = self.net.http_GET(web_url, headers).content
        r = re.search(r'window\.playerConfig\s*=\s*([^<]+)', html)
        if r:
            data = json.loads(r.group(1))
            hls = data.get('request', {}).get('files', {}).get('hls')
            if hls:
                src = hls.get('cdns', {}).get(hls.get('default_cdn'), {}).get('url')
                if src:
                    src_url = src + helpers.append_headers(headers)
                    if subs:
                        subtitles = {}
                        matches = data.get('request', {}).get('text_tracks')
                        if matches:
                            subtitles = {x.get('label'): urllib_parse.urljoin(ref, x.get('url')) for x in matches}
                        return src_url, subtitles
                    return src_url

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://player.vimeo.com/video/{media_id}')
