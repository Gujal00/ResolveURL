"""
    resolveurl XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

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
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError
import urlparse
import urllib
import json

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

class SimplyDebridResolver(ResolveUrl):
    name = "Simply-Debrid"
    domains = ["*"]
    base_url = 'https://simply-debrid.com/kapi.php?'

    def __init__(self):
        self.hosts = []
        self.patterns = []
        self.net = common.Net()
        self.username = self.get_setting('username')
        self.password = self.get_setting('password')
        self.token = None

    def get_media_url(self, host, media_id):
        if self.token is not None:
            try:
                query = urllib.urlencode({'action': 'generate', 'u': media_id, 'token': self.token})
                url = self.base_url + query
                response = self.net.http_GET(url).content
                if response:
                    js_result = json.loads(response)
                    logger.log_debug('SD: Result: %s' % (js_result))
                    if js_result['error']:
                        msg = js_result.get('message', 'Unknown Error')
                        raise ResolverError('SD Resolve Failed: %s' % (msg))
                    else:
                        return js_result['link']
            except Exception as e:
                raise ResolverError('SD Resolve: Exception: %s' % (e))

    def login(self):
        try:
            query = urllib.urlencode({'action': 'login', 'u': self.username, 'p': self.password})
            url = self.base_url + query
            response = self.net.http_GET(url).content
            js_result = json.loads(response)
            if js_result['error']:
                msg = js_result.get('message', 'Unknown Error')
                raise ResolverError('SD Login Failed: %s' % (msg))
            else:
                self.token = js_result['token']
        except Exception as e:
            raise ResolverError('SD Login Exception: %s' % (e))

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'simply-debrid.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
            query = urllib.urlencode({'action': 'filehosting'})
            url = self.base_url + query
            response = self.net.http_GET(url).content
            hosts = [i['domain'] for i in json.loads(response)]
            logger.log_debug('SD Hosts: %s' % (hosts))
        except Exception as e:
            logger.log_error('Error getting Simply-Debrid hosts: %s' % (e))
            hosts = []
        return hosts

    def valid_url(self, url, host):
        if not self.hosts:
            self.hosts = self.get_all_hosters()
            
        if url:
            try: host = urlparse.urlparse(url).hostname
            except: host = 'unknown'
        if host.startswith('www.'): host = host.replace('www.', '')
        if any(host in item for item in self.hosts):
            return True

        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="%s" default=""/>' % (cls.__name__, i18n('username')))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('password')))
        return xml

    @classmethod
    def isUniversal(self):
        return True
