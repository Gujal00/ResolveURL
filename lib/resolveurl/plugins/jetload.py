"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal

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

import json
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError


class JetloadResolver(ResolveUrl):
    name = 'jetload'
    domains = ['jetload.net', 'jetload.tv', 'jetload.to']
    pattern = r'(?://|\.)(jetload\.(?:net|tv|to))/(?:[a-zA-Z]/|.*?embed\.php\?u=)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.headers = {'User-Agent': common.SMR_USER_AGENT}

    def get_media_url(self, host, media_id):
        try:
            result = self.__check_auth(media_id)
            if not result:
                result = self.__auth_ip(media_id)
        except ResolverError:
            raise

        if result:
            return result + helpers.append_headers(self.headers)

        raise ResolverError("Unable to retrieve video")

    def __auth_ip(self, media_id):
        header = i18n('jetload_auth_header')
        line1 = i18n('auth_required')
        line2 = i18n('visit_link')
        line3 = i18n('click_pair') % 'https://jlpair.net/'
        with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
            return cd.start(self.__check_auth, [media_id])

    def __check_auth(self, media_id):
        common.logger.log('Checking Auth: %s' % media_id)
        url = 'https://jetload.net/api/fetch/%s' % media_id
        try:
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError:
            raise ResolverError('Unusable Authorization Response')

        if 'err' in js_result.keys():
            err_msg = js_result.get('err', '')
            if 'pair' in err_msg.lower():
                return False
            else:
                raise ResolverError('The requested video was not found or may have been removed.')

        if 'src' in js_result.keys():
            return js_result.get('src').get('src')
        else:
            return {}

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/e/{media_id}')

    @classmethod
    def isPopup(self):
        return True
