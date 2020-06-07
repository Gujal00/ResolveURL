"""
    Plugin for ResolveURL
    Copyright (C) 2019  script.module.resolveurl

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class GofileResolver(ResolveUrl):
    name = 'gofile'
    domains = ['gofile.io']
    pattern = r'(?://|\.)(gofile\.io)/(?:\?c=|d/)([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        download_serv = json.loads(self.net.http_GET('https://apiv2.' + host + '/getServer?c=' + media_id, headers=headers).content)
        if (download_serv['status'] == 'ok'):
            download_url = json.loads(self.net.http_GET('https://' + download_serv['data']['server'] + '.' + host + '/getUpload?c=' + media_id, headers=headers).content)
            sources = []
            if(download_url['data']['files']):
                for file_index in download_url['data']['files']:
                    url = urllib_parse.quote(download_url['data']['files'][file_index]['link'], ':/')
                    size = download_url['data']['files'][file_index]['size']
                    sources += [(size, url)]
            return helpers.pick_source(sources, False)
        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/?c={media_id}')
