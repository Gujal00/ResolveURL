"""
vshare.eu resolveurl plugin
Copyright (C) 2017 jsergio

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

import urllib2
import json
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError


class VshareEuResolver(ResolveUrl):
    name = "vshare.eu"
    domains = ['vshare.eu']
    pattern = '(?://|\.)(vshare\.eu)/(?:embed-|)?([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.SMR_USER_AGENT}

    def get_media_url(self, host, media_id):
        result = self.__check_auth(media_id)
        if not result:
            result = self.__auth_ip(media_id)

        if result:
            return helpers.pick_source(result.items()) + helpers.append_headers(self.headers)

        raise ResolverError(i18n('no_ip_authorization'))

    def __auth_ip(self, media_id):
        header = i18n('vshareeu_auth_header')
        line1 = i18n('auth_required')
        line2 = i18n('visit_link')
        line3 = i18n('click_pair') % ('http://vshare.eu/pair')
        with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
            return cd.start(self.__check_auth, [media_id])

    def __check_auth(self, media_id):
        common.logger.log('Checking Auth: %s' % (media_id))
        url = 'http://vshare.eu/cgi-bin/index_dl.fcgi?op=pair&file_code=%s&check' % (media_id)
        try:
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError:
            raise ResolverError('Unusable Authorization Response')
        except urllib2.HTTPError as e:
            if e.code == 401:
                js_result = json.loads(str(e.read()))
            else:
                raise

        common.logger.log('Auth Result: %s' % (js_result))
        if js_result.get('status') == 'true':
            return js_result.get('response', {})
        else:
            return False

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)

    @classmethod
    def isPopup(self):
        return True
