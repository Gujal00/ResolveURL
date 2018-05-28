"""
    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

class StreamintoResolver(ResolveUrl):
    name = "streaminto"
    domains = ["streamin.to"]
    pattern = '(?://|\.)(streamin\.to)/(?:embed-|)?([0-9A-Za-z]+)'
    
    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.SMR_USER_AGENT}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url}
        headers.update(self.headers)
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.scrape_sources(html, patterns=["""file:\s*["'](?P<url>[^"']+)"""])
        if sources:
            auth = self.__check_auth(media_id)
            if not auth:
                auth = self.__auth_ip(media_id)
                
            if auth:
                return helpers.pick_source(sources) + helpers.append_headers(headers)
            else:
                raise ResolverError(i18n('no_ip_authorization'))
        else:
            raise ResolverError('Unable to locate links')

    def __auth_ip(self, media_id):
        header = i18n('stream_auth_header')
        line1 = i18n('auth_required')
        line2 = i18n('visit_link')
        line3 = i18n('click_pair') % ('http://api.streamin.to/pair')
        with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
            return cd.start(self.__check_auth, [media_id])
        
    def __check_auth(self, media_id):
        common.logger.log('Checking Auth: %s' % (media_id))
        url = 'http://api.streamin.to/pair/check.php'
        try: js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError: raise ResolverError('Unusable Authorization Response')
        common.logger.log('Auth Result: %s' % (js_result))
        return js_result.get('status') == 200
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
