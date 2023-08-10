"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class DaxabResolver(ResolveUrl):
    name = 'Daxab'
    domains = ['daxab.com']
    pattern = r'(?://|\.)(daxab\.com)/player/([^\n]+)'

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
        html = self.net.http_GET(web_url, headers=headers).content
        params = re.search(r'video:\s*([^;]+)', html)
        if params:
            params = params.group(1)
            server = re.findall(r'server:\s*"([^"]+)', params)[0][::-1]
            server = helpers.b64decode(server.encode('ascii'))
            ids = re.search(r'cdn_id:\s*"([^"]+)', params)
            if ids:
                id1, id2 = ids.group(1).split('_')
                sources = json.loads(re.findall(r'cdn_files:\s*([^}]+})', params)[0])
                sources = [
                    (key[4:], 'https://{0}/videos/{1}/{2}/{3}'.format(
                        server, id1, id2, sources[key].replace('.', '.mp4?extra=')))
                    for key in list(sources.keys())
                ]
            else:
                vid = re.findall(r'id:\s*"([^"]+)', params)[0]
                ekeys = json.loads(re.findall(r'quality":\s*([^}]+})', params)[0])
                data = {
                    'token': re.findall(r'access_token:\s*"([^"]+)', params)[0],
                    'videos': vid,
                    'ckey': re.findall(r'c_key:\s*"([^"]+)', params)[0],
                    'credentials': re.findall(r'credentials:\s*"([^"]+)', params)[0]
                }
                vurl = 'https://{0}/method/video.get/{1}?{2}'.format(server, vid, urllib_parse.urlencode(data))
                headers.update({'Origin': referer[:-1]})
                vhtml = self.net.http_GET(vurl, headers=headers).content
                sources = json.loads(vhtml).get('response').get('items')[0].get('files')
                sources = [(key[4:], sources[key] + '&videos={0}&extra_key={1}&videos={0}'.format(vid, ekeys[key[4:]]))
                           for key in list(sources.keys()) if key[4:] in ekeys.keys()]

            source = helpers.pick_source(sorted(sources, reverse=True))
            if 'extra_key' in source:
                source = source.replace('https://', 'https://{0}/'.format(server))

            return source + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/{media_id}')
