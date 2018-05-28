"""
    ResolveURL Addon for Kodi
    Copyright (C) 2016 t0mm0, tknorris

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
import urllib2
import json
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

CLIENT_ID = 'MUQMIQX6YWDSU'
USER_AGENT = 'ResolveURL for Kodi/%s' % (common.addon_version)
INTERVALS = 5


class RealDebridResolver(ResolveUrl):
    name = "Real-Debrid"
    domains = ["*"]

    def __init__(self):
        self.net = common.Net()
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id, retry=False):
        try:
            url = 'https://api.real-debrid.com/rest/1.0/unrestrict/link'
            headers = self.headers
            headers['Authorization'] = 'Bearer %s' % (self.get_setting('token'))
            data = {'link': media_id}
            result = self.net.http_POST(url, form_data=data, headers=headers).content
        except urllib2.HTTPError as e:
            if not retry and e.code == 401:
                if self.get_setting('refresh'):
                    self.refresh_token()
                    return self.get_media_url(host, media_id, retry=True)
                else:
                    self.reset_authorization()
                    raise ResolverError('Real Debrid Auth Failed & No Refresh Token')
            else:
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = js_result['error']
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise ResolverError('Real Debrid Error: %s (%s)' % (msg, e.code))
        except Exception as e:
            raise ResolverError('Unexpected Exception during RD Unrestrict: %s' % (e))
        else:
            js_result = json.loads(result)
            links = []
            link = self.__get_link(js_result)
            if link is not None: links.append(link)
            if 'alternative' in js_result:
                for alt in js_result['alternative']:
                    link = self.__get_link(alt)
                    if link is not None: links.append(link)

            return helpers.pick_source(links)

    def __get_link(self, link):
        if 'download' in link:
            if 'quality' in link:
                label = '[%s] %s' % (link['quality'], link['download'])
            else:
                label = link['download']
            return (label, link['download'])

    # SiteAuth methods
    def login(self):
        if not self.get_setting('token'):
            self.authorize_resolver()

    def refresh_token(self):
        client_id = self.get_setting('client_id')
        client_secret = self.get_setting('client_secret')
        refresh_token = self.get_setting('refresh')
        logger.log_debug('Refreshing Expired Real Debrid Token: |%s|%s|' % (client_id, refresh_token))
        if not self.__get_token(client_id, client_secret, refresh_token):
            # empty all auth settings to force a re-auth on next use
            self.reset_authorization()
            raise ResolverError('Unable to Refresh Real Debrid Token')

    def authorize_resolver(self):
        url = 'https://api.real-debrid.com/oauth/v2/device/code?client_id=%s&new_credentials=yes' % (CLIENT_ID)
        js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        line1 = 'Go to URL: %s' % (js_result['verification_url'])
        line2 = 'When prompted enter: %s' % (js_result['user_code'])
        with common.kodi.CountdownDialog('Resolve URL Real Debrid Authorization', line1, line2, countdown=120, interval=js_result['interval']) as cd:
            result = cd.start(self.__check_auth, [js_result['device_code']])

        # cancelled
        if result is None: return
        return self.__get_token(result['client_id'], result['client_secret'], js_result['device_code'])
        
    def __get_token(self, client_id, client_secret, code):
        try:
            url = 'https://api.real-debrid.com/oauth/v2/token'
            data = {'client_id': client_id, 'client_secret': client_secret, 'code': code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
            self.set_setting('client_id', client_id)
            self.set_setting('client_secret', client_secret)
            logger.log_debug('Authorizing Real Debrid: %s' % (client_id))
            js_result = json.loads(self.net.http_POST(url, data, headers=self.headers).content)
            logger.log_debug('Authorizing Real Debrid Result: |%s|' % (js_result))
            self.set_setting('token', js_result['access_token'])
            self.set_setting('refresh', js_result['refresh_token'])
            return True
        except Exception as e:
            logger.log_debug('Real Debrid Authorization Failed: %s' % (e))
            return False

    def __check_auth(self, device_code):
        try:
            url = 'https://api.real-debrid.com/oauth/v2/device/credentials?client_id=%s&code=%s' % (CLIENT_ID, device_code)
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except Exception as e:
            logger.log_debug('Exception during RD auth: %s' % (e))
        else:
            return js_result

    def reset_authorization(self):
        self.set_setting('client_id', '')
        self.set_setting('client_secret', '')
        self.set_setting('token', '')
        self.set_setting('refresh', '')
    
    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.real-debrid.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
            hosters = []
            url = 'https://api.real-debrid.com/rest/1.0/hosts/regex'
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
            regexes = [regex[1:-1].replace('\/', '/').rstrip('\\') for regex in js_result]
            logger.log_debug('RealDebrid hosters : %s' % (regexes))
            hosters = [re.compile(regex) for regex in regexes]
        except Exception as e:
            logger.log_error('Error getting RD regexes: %s' % (e))
        return hosters

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        try:
            hosts = []
            url = 'https://api.real-debrid.com/rest/1.0/hosts/domains'
            hosts = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except Exception as e:
            logger.log_error('Error getting RD hosts: %s' % (e))
        logger.log_debug('RealDebrid hosts : %s' % (hosts))
        return hosts

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    def valid_url(self, url, host):
        logger.log_debug('in valid_url %s : %s' % (url, host))
        if url:
            if self.hosters is None:
                self.hosters = self.get_all_hosters()
                
            for host in self.hosters:
                # logger.log_debug('RealDebrid checking host : %s' %str(host))
                if re.search(host, url):
                    logger.log_debug('RealDebrid Match found')
                    return True
        elif host:
            if self.hosts is None:
                self.hosts = self.get_hosts()
                
            if host.startswith('www.'): host = host.replace('www.', '')
            if any(host in item for item in self.hosts):
                return True
        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_autopick" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('auto_primary_link')))
        xml.append('<setting id="%s_auth" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_rd)"/>' % (cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="%s_reset" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_rd)"/>' % (cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="%s_token" visible="false" type="text" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_refresh" visible="false" type="text" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_client_id" visible="false" type="text" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_client_secret" visible="false" type="text" default=""/>' % (cls.__name__))
        return xml

    @classmethod
    def isUniversal(self):
        return True
