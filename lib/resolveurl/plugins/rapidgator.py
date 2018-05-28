"""
Copyright (C) 2017 kodistuff1

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

import json, urllib
from urllib2 import HTTPError
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

class RapidgatorResolver(ResolveUrl):
    name = 'Rapidgator'
    domains = ['rapidgator.net', 'rg.to']
    pattern = '(?://|\.)(rapidgator\.net|rg\.to)/+file/+([a-z0-9]+)(?=[/?#]|$)'

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('login') == 'true' and cls.get_setting('premium') == 'true'

    def __init__(self):
        self.net = common.Net()
        self.scheme = 'https'
        self.api_base = '%s://rapidgator.net/api' % (self.scheme)
        self._session_id = ''

    def login(self):
        if not (self.get_setting('login') == 'true'):
            return False
        self._session_id = self.get_setting('session_id')
        return True

    def logout(self):
        self._session_id = ''
        self.set_setting('session_id', '')

    def api_call(self, method, data, http='GET', session=True, refresh=True):
        loop = 0
        while loop < 2:
            loop += 1

            if session:
                data.update({'sid': self._session_id})

            try:
                if http == 'GET':
                    content = self.net.http_GET(self.api_base + method + '?' + urllib.urlencode(data)).content
                elif http == 'HEAD':
                    content = self.net.http_HEAD(self.api_base + method + '?' + urllib.urlencode(data)).content
                elif http == 'POST':
                    content = self.net.http_POST(self.api_base + method, urllib.urlencode(data)).content
                else:
                    raise ResolverError(self.name + ' Bad Request')

                content = json.loads(content)
                status = int(content['response_status'])
                response = content['response']
            except HTTPError as e:
                status, response = e.code, []
            except ResolverError:
                raise
            except:
                raise ResolverError(self.name + ' Bad Response')

            if status == 200:
                return response

            if session and refresh and status in [401,402]: # only actually seen 401, although 402 seems plausible
                self.refresh_session()
                continue

            raise ResolverError(self.name + ' HTTP ' + str(status) + ' Error')

    def refresh_session(self):
        if not (self.get_setting('login') == 'true'):
            return False
        username, password = self.get_setting('username'), self.get_setting('password')
        if not (username and password):
            raise ResolverError(self.name + ' username & password required')
        data = {'username': username, 'password': password}
        try:
            response = self.api_call('/user/login', data, http='POST', session=False)
            self._session_id = response['session_id']
        except:
            self._session_id = ''
        self.set_setting('session_id', self._session_id)
        return True if self._session_id else False

    def get_media_url(self, host, media_id):
        if not (self.get_setting('premium') == 'true'):
            raise ResolverError(self.name + ' premium account required')
        data = {'url': self.get_url(host, media_id)}
        response = self.api_call('/file/download', data)
        if 'delay' in response and response['delay'] and response['delay'] != '0':
            raise ResolverError(self.name + ' premium account expired')
        if 'url' not in response:
            raise ResolverError(self.name + ' Bad Response')
        return response['url'].replace('\\', '')

    def get_url(self, host, media_id):
        return '%s://%s/file/%s' % (self.scheme, host, media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="%s" default=""/>' % (cls.__name__, i18n('username')))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('password')))
        xml.append('<setting id="%s_premium" enable="eq(-3,true)" type="bool" label="Premium Account" default="false"/>' % (cls.__name__))
        xml.append('<setting id="%s_session_id" visible="false" type="text" default=""/>' % (cls.__name__))
        return xml
