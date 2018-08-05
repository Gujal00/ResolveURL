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

import re
import urllib
import urllib2
import json
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

AGENT = 'ResolveURL for Kodi'
VERSION = common.addon_version
USER_AGENT = '%s/%s' % (AGENT, VERSION)


class AllDebridResolver(ResolveUrl):
    name = "AllDebrid"
    domains = ['*']

    def __init__(self):
        self.net = common.Net()
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id):
        url = 'https://api.alldebrid.com/link/unlock?agent=%s&version=%s&token=%s&link=%s' % (urllib.quote_plus(AGENT), urllib.quote_plus(VERSION), self.get_setting('token'), media_id)
        try:
            result = self.net.http_GET(url, headers=self.headers).content
        except urllib2.HTTPError as e:
            try:
                js_result = json.loads(e.read())
                if 'error' in js_result:
                    msg = '%s (%s)' % (js_result.get('error'), js_result.get('errorCode'))
                else:
                    msg = 'Unknown Error (1)'
            except:
                msg = 'Unknown Error (2)'
            raise ResolverError('AllDebrid Error: %s (%s)' % (msg, e.code))
        else:
            js_result = json.loads(result)
            logger.log_debug('AllDebrid resolve: [%s]' % js_result)
            if 'error' in js_result:
                raise ResolverError('AllDebrid Error: %s (%s)' % (js_result.get('error'), js_result.get('errorCode')))
            elif js_result.get('success', False):
                if js_result.get('infos').get('link'):
                    return js_result.get('infos').get('link')
        raise ResolverError('AllDebrid: no stream returned')

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.alldebrid.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        hosters = []
        url = 'https://api.alldebrid.com/user/hosts?agent=%s&version=%s&token=%s' % (urllib.quote_plus(AGENT), urllib.quote_plus(VERSION), self.get_setting('token'))
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get('success', False):
                regexes = [value.get('regexp').replace('\/', '/') for key, value in js_data.get('hosts', {}).iteritems()
                           if value.get('status', False)]
                logger.log_debug('AllDebrid hosters : %s' % regexes)
                hosters = [re.compile(regex) for regex in regexes]
            else:
                logger.log_error('Error getting AD Hosters')
        except Exception as e:
            logger.log_error('Error getting AD Hosters: %s' % e)
        return hosters

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        url = 'https://api.alldebrid.com/hosts/domains'
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get('success', False):
                hosts = [host.replace('www.', '') for host in js_data.get('hosts', [])]
                logger.log_debug('AllDebrid hosts : %s' % hosts)
            else:
                logger.log_error('Error getting AD Hosters')
        except Exception as e:
            logger.log_error('Error getting AD Hosts: %s' % e)
        return hosts

    def valid_url(self, url, host):
        logger.log_debug('in valid_url %s : %s' % (url, host))
        if url:
            if self.hosters is None:
                self.hosters = self.get_all_hosters()

            for regexp in self.hosters:
                # logger.log_debug('AllDebrid checking host : %s' %str(regexp))
                if re.search(regexp, url):
                    logger.log_debug('AllDebrid Match found')
                    return True
        elif host:
            if self.hosts is None:
                self.hosts = self.get_hosts()

            if any(host in item for item in self.hosts):
                return True

        return False

    # SiteAuth methods
    def login(self):
        if not self.get_setting('token'):
            self.authorize_resolver()

    def reset_authorization(self):
        self.set_setting('token', '')

    def authorize_resolver(self):
        url = 'https://api.alldebrid.com/pin/get?agent=%s&version=%s' % (urllib.quote_plus(AGENT), urllib.quote_plus(VERSION))
        js_result = self.net.http_GET(url, headers=self.headers).content
        js_data = json.loads(js_result)
        line1 = 'Go to URL: %s' % (js_data.get('base_url').replace('\/', '/'))
        line2 = 'When prompted enter: %s' % (js_data.get('pin'))
        with common.kodi.CountdownDialog('Resolve Url All Debrid Authorization', line1, line2,
                                         countdown=js_data.get('expired_in', 120)) as cd:
            result = cd.start(self.__check_auth, [js_data.get('check_url').replace('\/', '/')])

        # cancelled
        if result is None:
            return
        return self.__get_token(js_data.get('check_url').replace('\/', '/'))

    def __get_token(self, url):
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get("success", False):
                token = js_data.get('token', '')
                logger.log_debug('Authorizing All Debrid Result: |%s|' % token)
                self.set_setting('token', token)
                return True
        except Exception as e:
            logger.log_debug('All Debrid Authorization Failed: %s' % e)
            return False

    def __check_auth(self, url):
        activated = False
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get("success", False):
                activated = js_data.get('activated', False)
        except Exception as e:
            logger.log_debug('Exception during AD auth: %s' % e)
        return activated

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        # xml.append('<setting id="%s_autopick" type="bool" label="%s" default="false"/>' % (
        #    cls.__name__, i18n('auto_primary_link')))
        xml.append(
            '<setting id="%s_auth" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_ad)"/>' % (
                cls.__name__, i18n('auth_my_account')))
        xml.append(
            '<setting id="%s_reset" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_ad)"/>' % (
                cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="%s_token" visible="false" type="text" default=""/>' % cls.__name__)
        return xml

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    @classmethod
    def isUniversal(self):
        return True
