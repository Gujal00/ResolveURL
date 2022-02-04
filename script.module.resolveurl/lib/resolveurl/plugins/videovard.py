'''
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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
'''

from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.plugins.lib import helpers
import json


class VideoVardResolver(ResolveUrl):
    name = "videovard"
    domains = ["videovard.sx", "videovard.to"]
    pattern = r'(?://|\.)(videovard\.(?:sx|to))/[ved]/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        surl = 'https://{0}/'.format(host)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': surl
        }
        html = self.net.http_GET(web_url, headers=headers).content
        html = json.loads(html)
        r = html.get('hash', '')
        if r:
            url = 'https://{0}/api/player/setup'.format(host)
            data = {
                'cmd': 'get_stream',
                'file_code': media_id,
                'hash': r
            }
            headers.update({'Origin': surl[:-1]})
            resp = self.net.http_POST(url, form_data=data, headers=headers).content
            resp = json.loads(resp)
            vfile = resp.get('src')
            seed = resp.get('seed')
            source = helpers.tear_decode(vfile, seed)
            if source:
                return source + helpers.append_headers(headers)
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/api/make/hash/{media_id}')
