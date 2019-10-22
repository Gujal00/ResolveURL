"""
    Kodi resolveurl plugin
    Copyright (C) 2018  script.module.resolveurl

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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class GofileResolver(ResolveUrl):
    name = 'gofile'
    domains = ['gofile.io']
    pattern = '(?://|\.)(gofile\.io)/\?c=([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        try:
            web_url = self.get_url(host, media_id)
            headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
            download_serv = json.loads( self.net.http_GET('https://apiv2.gofile.io/getServer?c=' + media_id, headers=headers).content )
            if ( download_serv['status'] == 'ok' ):
                download_url = json.loads( self.net.http_GET('https://' + download_serv['data']['server'] + '.gofile.io/getUpload?c=' + media_id, headers=headers).content )
                return download_url['data']['files']['0']['link']
        except:
            raise ResolverError('Unable to locate video')
        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return 'https://gofile.io/?c=%s' % (media_id)
