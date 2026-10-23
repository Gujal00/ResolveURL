"""
    Plugin for ResolveURL
    Copyright (C) 2026 TempleLain

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

from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class ContentStResolver(ResolveUrl):
    name = 'ContentSt'
    domains = ['content.st']
    pattern = r'(?://|\.)(content\.st)/(?:e|v)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': web_url,
            'Origin': 'https://{0}'.format(host)
        }
        # The embed page carries no stream address (its config has src:null,
        # needCheck:true); it is handed out by POST /x/k/<id> once the client-side
        # ad-block check is clean. The check result is a plain string in the body:
        # an empty string means "no ad blocker", which is what a player loads with.
        api_url = 'https://{0}/x/k/{1}'.format(host, media_id)
        data = self.net.http_POST(api_url, form_data={'bc': ''}, headers=headers, jdata=True).json
        if data and data.get('ok') and data.get('src'):
            headers.pop('Origin', None)
            headers['Referer'] = 'https://{0}/'.format(host)
            return data.get('src') + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
