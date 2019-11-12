"""
    Kodi resolveurl plugin
    Copyright (C) 2016  script.module.resolveurl

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

     Resolver JETLOAD - 31.05.2019 - RC 1 incl. select resolution 
"""
import re
import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class JetloadResolver(ResolveUrl):
    name = 'jetload'
    domains = ['jetload.net']
    pattern = '(?://|\.)(jetload\.(?:net|tv|to))/(?:[a-zA-Z]/|embed\.php\?u=)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content.encode('utf-8')

        try:
            url = re.findall('source src="(.*?)"', html)[0]
            if '.m3u8' in url:
                m3u = self.net.http_GET(url, headers=headers).content
            else:
                return url + helpers.append_headers(headers)
        except:
            jsons = json.loads(html)
            hostname = jsons['server']['hostname']
            filename = jsons['file']['file_name']
            url = hostname + '/v2/schema/archive/' + filename + '/master.m3u8'
            m3u = self.net.http_GET(url, headers=headers).content

        streams = re.findall(r'(.*?)\.m3u8', m3u)
        qualitys = re.findall(r'RESOLUTION=(.*?)\n', m3u)

        stream = (streams[len(streams) - 1] + '.m3u8').replace(' ', '')
        if '1080' in qualitys[len(streams) - 1]:
            quality = '1080p'
        elif '720' in qualitys[len(streams) - 1]:
            quality = '720p'
        else:
            quality = 'SD'

        return url + '?quali=' + quality + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/p/{media_id}')
