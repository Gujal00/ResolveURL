"""
    Plugin for ResolveURL
    Copyright (C) 2018 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
import base64
import six
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class TubePornClassicResolver(ResolveUrl):
    name = 'tubepornclassic'
    domains = ['tubepornclassic.com']
    pattern = r'(?://|\.)(tubepornclassic\.com)/videos/(\d+/[^/\s]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.RAND_UA}
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search('''video_url=['"]([^'"]+)['"]''', html, re.DOTALL)
        replaceparts = re.search(r'''video_url\+=['"]([^'"]+)['"]''', html, re.DOTALL)

        if r:
            source = r.group(1)
            replacemap = {'M': u'\u041C', 'A': u'\u0410', 'B': u'\u0412', 'C': u'\u0421', 'E': u'\u0415', '=': '~'}
            for key in replacemap:
                source = source.replace(replacemap[key], key)
            source = source.encode('ascii') if six.PY3 else source
            videourl = base64.b64decode(source)
            videourl = videourl.decode('latin-1') if six.PY3 else videourl
            if replaceparts:
                replaceparts = [x for x in replaceparts.group(1).split('||') if x]
                videourl = re.sub(r'/get_file/\d+/[0-9a-z]{32}/', replaceparts[0], videourl)
                videourl += '&' if '?' in videourl else '?'
                videourl += 'lip=' + replaceparts[1] + '&lt=' + replaceparts[2]
                return self.net.http_GET(videourl, headers=headers).get_url() + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/videos/{media_id}/')

    @classmethod
    def _is_enabled(cls):
        return True
