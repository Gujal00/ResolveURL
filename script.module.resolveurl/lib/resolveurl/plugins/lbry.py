"""
    Plugin for ResolveURL
    Copyright (C) 2021  script.module.resolveurl

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class LbryResolver(ResolveUrl):
    name = 'lbry'
    domains = ['lbry.tv','odysee.com','madiator.com']
    pattern = r'(?://|\.)(lbry\.tv|odysee\.com|madiator\.com)/(\@[^:\/]+\:[^:\/]+\/[^:\/]+:[0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        form_data = {'jsonrpc':'2.0','method':'get','params':{'uri':'lbry://' + (media_id).replace(':', '#'),'save_file':False}}
        headers = {'User-Agent': common.FF_USER_AGENT, 'Origin': 'https://lbry.tv', 'Referer': web_url}
        response = json.loads(self.net.http_POST('https://api.lbry.tv/api/v1/proxy?m=get', form_data=form_data, headers=headers, jdata=True).content)
        if ( response['result']['streaming_url'] ):
            return response['result']['streaming_url']
        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://lbry.tv/{media_id}')
