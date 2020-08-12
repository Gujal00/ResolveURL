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
import json
from six.moves import urllib_error
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VidUpResolver(ResolveUrl):
    name = "vidup.me"
    domains = ["vidup.me", "vidup.tv", "vidup.io", "vidop.icu"]
    pattern = r'(?://|\.)(vid[ou]p\.(?:me|tv|io|icu))/(?:embed-|download/|embed/)?([0-9a-zA-Z]+)'

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
            return helpers.pick_source(helpers.sort_sources_list(result)) + helpers.append_headers(self.headers)

        raise ResolverError("Unable to retrieve video")

    def __auth_ip(self, media_id):
        header = i18n('vidup_auth_header')
        line1 = i18n('auth_required')
        line2 = i18n('visit_link')
        line3 = i18n('click_pair') % 'https://vidop.icu/pair'
        with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
            return cd.start(self.__check_auth, [media_id])

    def __check_auth(self, media_id):
        common.logger.log('Checking Auth: %s' % media_id)
        url = self.get_url(media_id)
        try:
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError:
            raise ResolverError('Unusable Authorization Response')
        except urllib_error.HTTPError as e:
            if e.code == 400:
                msg = e.read().decode("utf8")
                if 'invalid video specified' in msg:
                    raise ResolverError('Video Link Not Found')
                js_result = {}
            else:
                raise ResolverError('Unusable Authorization Response')

        common.logger.log('Auth Result: %s' % js_result)
        if js_result.get('qualities', {}):
            return [(qual.get('size')[1], qual.get('src')) for qual in js_result.get('qualities')]
        else:
            return []

    def get_url(self, media_id, host='vidop.icu'):
        return self._default_get_url(host, media_id, template='https://{host}/api/pair/{media_id}')

    @classmethod
    def isPopup(self):
        return True
