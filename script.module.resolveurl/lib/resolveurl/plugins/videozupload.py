"""
    Plugin for ResolveUrl
    Copyright (C) 2018 gujal

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

from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.plugins.lib import unwise
import re


class VideozUpload(ResolveUrl):
    name = 'videozupload.net'
    domains = ['videozupload.net', 'videzup.pl', 'videzup.top']
    pattern = r'(?://|\.)((?:videozupload|videzup)\.(?:net|pl|top))/video/([0-9a-z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        html = unwise.unwise_process(html)
        r = re.search(r"Clappr.+?source:\s*'([^']+)", html)
        if r:
            headers.update({'Referer': web_url})
            return r.group(1) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://embed.{host}/video/{media_id}')
