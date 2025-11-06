"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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


class BunnyResolver(ResolveUrl):
    name = 'Bunny'
    domains = ['mediadelivery.net']
    pattern = r'(?://|\.)(mediadelivery\.net)/embed/([0-9a-z-=$:/.?&]+)'

    def get_media_url(self, host, media_id, subs=False):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        web_ref = urllib_parse.urljoin(web_url, '/')
        if not referer:
            referer = web_ref
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'<source.+?src="([^"]+)', html)
        if r:
            headers.update({'Referer': web_ref, 'Origin': web_ref[:-1]})
            url = r.group(1) + helpers.append_headers(headers)
            if subs:
                subtitles = {}
                s = re.findall(r'''<track\s*kind\s*=\s*'captions'\s*label\s*=\s*'([^']+)'\s*src\s*=\s*'([^']+)''', html)
                if s:
                    subtitles = {lang: sub for lang, sub in s}
                return url, subtitles
            return url

        raise ResolverError("Unable to locate stream URL.")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://iframe.{host}/embed/{media_id}')
