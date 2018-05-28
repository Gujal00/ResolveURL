"""
    resolveurl Kodi Addon

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

import os
import re
import urllib2
import json
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

AGENT = 'ResolveURL.Kodi'


class AllDebridResolver(ResolveUrl):
    name = "AllDebrid"
    domains = ['*']
    profile_path = common.profile_path
    cookie_file = os.path.join(profile_path, '%s.cookies' % name)
    media_url = None

    def __init__(self):
        self.hosts = None
        self.net = common.Net()
        try:
            os.makedirs(os.path.dirname(self.cookie_file))
        except OSError:
            pass

    def get_media_url(self, host, media_id):
        try:
            token = self.get_setting('token')
            url = 'https://api.alldebrid.com/link/unlock?agent=%s&token=%s&link=%s' % (AGENT, token, media_id)
            if token:
                result = self.net.http_GET(url).content
        except urllib2.HTTPError as e:
            if e.code == 401:
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = ('%s (%s)') % (js_result['error'], js_result['errorCode'])
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise ResolverError('AllDebrid Error: %s (%s)' % (msg, e.code))
            else:
                raise ResolverError('AllDebrid Error: Unknown Error (3)')
        except Exception as e:
            raise ResolverError('Unexpected Exception during AD Unrestrict: %s' % (e))
        else:
            js_result = json.loads(result)
            logger.log_debug('AllDebrid resolve: [%s]' % js_result)
            if 'error' in js_result:
                common.kodi.notify(msg=str(js_result['error']), duration=5000)
                raise ResolverError('AllDebrid Error: %s (%s)' % (js_result['error'], js_result['errorCode']))
            elif js_result['success']:
                if js_result['infos']['link']:
                    return js_result['infos']['link']
                else:
                    raise ResolverError('alldebrid: no stream returned')    
            else:
                raise ResolverError('alldebrid: no stream returned')

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.alldebrid.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        url = 'https://api.alldebrid.com/hosts/domains'
        html = self.net.http_GET(url).content
        js_data = json.loads(html)
        return js_data['hosts']

    def valid_url(self, url, host):
        if self.hosts is None:
            self.hosts = self.get_all_hosters()
            
        logger.log_debug('in valid_url %s : %s' % (url, host))
        if url:
            match = re.search('//(.*?)/', url)
            if match:
                host = match.group(1)
            else:
                return False

        if host.startswith('www.'): host = host.replace('www.', '')
        if host and any(host in item for item in self.hosts):
            return True

        return False

    # SiteAuth methods
    def login(self):
        if self.get_setting('username') and self.get_setting('password') and not self.get_setting('token'):
            self.authorize_resolver()

    def reset_authorization(self):
        self.set_setting('token', '')

    def authorize_resolver(self):
        try:
            self.reset_authorization()
            username = self.get_setting('username')
            password = self.get_setting('password')
            if username and password:
                url = 'https://api.alldebrid.com/user/login?agent=%s&username=%s&password=%s' % (AGENT, username, password)
                logger.log_debug('Authorizing AllDebrid')
                js_result = json.loads(self.net.http_GET(url).content)
        except urllib2.HTTPError as e:
            if e.code == 401:
                common.kodi.notify(msg='Invalid username or password', duration=5000)
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = ('%s (%s)' % (js_result['error'], js_result['errorCode']))
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise ResolverError('AllDebrid Error: %s (%s)' % (msg, e.code))
            elif e.code == 429:
                common.kodi.notify(msg='Please login on the Alldebrid website', duration=5000)
                raise ResolverError('AllDebrid Error: blocked login (flood)')
            else:
                raise ResolverError('AllDebrid Error: Unknown Error (3)')
        except Exception as e:
            raise ResolverError('Unexpected Exception during AD Login: %s' % (e))
        else:
            logger.log_debug('Authorizing AllDebrid Result: |%s|' % (js_result))
            if 'error' in js_result:
                raise ResolverError('AllDebrid Error: %s (%s)' % (js_result['error'], js_result['errorCode']))
            elif js_result['success']:
                self.set_setting('token', js_result['token'])

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="%s" default=""/>' % (cls.__name__, i18n('username')))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('password')))
        xml.append('<setting id="%s_auth" type="action" label="%s" enable="!eq(-1,)+!eq(-2,)+!eq(-3,false)" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_ad)"/>' % (cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="%s_reset" type="action" label="%s" enable="!eq(-2,)+!eq(-3,)+!eq(-4,false)" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_ad)"/>' % (cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="%s_token" visible="false" type="text" default=""/>' % (cls.__name__))
        return xml

    @classmethod
    def isUniversal(self):
        return True
