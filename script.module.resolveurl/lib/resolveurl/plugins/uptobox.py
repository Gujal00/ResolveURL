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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()


class UpToBoxResolver(ResolveUrl):
    name = "UpToBox"
    domains = ["uptobox.com", "uptostream.com"]
    pattern = r'(?://|\.)(uptobox.com|uptostream.com)/(?:iframe/)?([0-9A-Za-z_]+)'

    def __init__(self):
        self.headers = {'User-Agent': common.RAND_UA}

    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        if result.get('message') == 'Success':
            js_data = result.get('data')
            if 'streamLinks' in js_data.keys():
                js_result = result
            else:
                heading = i18n('uptobox_auth_header')
                line1 = i18n('auth_required')
                line2 = i18n('upto_link').format(js_data.get('base_url'))
                line3 = i18n('upto_pair').format(js_data.get('pin'))
                with common.kodi.CountdownDialog(heading, line1, line2, line3, True, js_data.get('expired_in'), 10) as cd:
                    js_result = cd.start(self.__check_auth, [js_data.get('check_url')])
                if js_result and js_result.get('data', {}).get('token'):
                    self.set_setting('token', js_result.get('data').get('token'))
                    self.set_setting('premium', 'true')
            if js_result:
                js_result = js_result.get('data').get('streamLinks')
                if isinstance(js_result, list):
                    sources = [(key, list(js_result.get(key).values())[0]) for key in list(js_result.keys())]
                    source = helpers.pick_source(helpers.sort_sources_list(sources))
                else:
                    source = js_result.get('src')
                return source + helpers.append_headers(self.headers)

        raise ResolverError('The requested video was not found or may have been removed.')

    def get_url(self, host, media_id):
        url = self._default_get_url(host, media_id, 'https://uptobox.com/api/streaming?file_code={media_id}')
        if self.get_setting('premium') == 'true':
            url += '&token={0}'.format(self.get_setting('token'))
        return url

    @classmethod
    def isPopup(self):
        return self.get_setting('premium') == 'false'

    # SiteAuth methods
    def reset_authorization(self):
        self.set_setting('token', '')
        self.set_setting('premium', 'false')

    def authorize_resolver(self):
        url = 'https://uptobox.com/api/streaming'
        js_data = json.loads(self.net.http_GET(url, headers=self.headers).content)
        if js_data.get('message') == 'Success':
            js_data = js_data.get('data')
            heading = i18n('uptobox_auth_header')
            line1 = i18n('auth_required')
            line2 = i18n('upto_link').format(js_data.get('base_url'))
            line3 = i18n('upto_pair').format(js_data.get('pin'))
            with common.kodi.CountdownDialog(heading, line1, line2, line3, True, js_data.get('expired_in'), 10) as cd:
                js_result = cd.start(self.__check_auth, [js_data.get('check_url')])

            # cancelled
            if js_result is None:
                return
            return self.__get_token(js_result)
        raise ResolverError('Error during authorisation.')

    def __get_token(self, js_data):
        try:
            if js_data.get("message") == "Success":
                js_data = js_data.get('data')
                token = js_data.get('token')
                logger.log_debug('Authorizing Uptobox Result: |{0}|'.format(token))
                self.set_setting('token', token)
                self.set_setting('premium', 'true')
                return True
        except Exception as e:
            logger.log_debug('Uptobox Authorization Failed: {0}'.format(e))
            return False

    def __check_auth(self, url):
        try:
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError:
            raise ResolverError('Unusable Authorization Response')

        if js_result.get('statusCode') == 0:
            if js_result.get('data') == "wait-pin-validation":
                return False
            else:
                return js_result

        raise ResolverError('Error during check authorisation.')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="{0}_premium" enable="false" label="{1}" type="bool" default="false"/>'.format(cls.__name__, i18n('ub_authorized')))
        xml.append('<setting id="{0}_auth" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_ub)"/>'.format(cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="{0}_reset" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_ub)"/>'.format(cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="{0}_token" visible="false" type="text" default=""/>'.format(cls.__name__))
        return xml
