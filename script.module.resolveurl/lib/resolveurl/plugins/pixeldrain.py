"""
    Plugin for ResolveURL
    Copyright (C) 2022 gujal

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class PixelDrainResolver(ResolveUrl):
    name = 'PixelDrain'
    domains = ['pixeldrain.com']
    pattern = r'(?://|\.)(pixeldrain\.com)/((?:u|l)/[0-9a-zA-Z\-]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers).content
        jd = json.loads(html)

        if jd.get('success'):
            if media_id.startswith('l/'):
                sources = [
                    (x.get('name'), x.get('id'))
                    for x in jd.get('files')
                    if 'video' in x.get('mime_type')
                ]
                return 'https://{0}/api/file/{1}'.format(host, helpers.pick_source(sources, False))
            else:
                return 'https://{0}/api/file/{1}'.format(host, media_id[2:])

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        mtype, mid = media_id.split('/')
        if mtype == 'u':
            return 'http://{0}/api/file/{1}/info'.format(host, mid)
        return 'http://{0}/api/list/{1}'.format(host, mid)
