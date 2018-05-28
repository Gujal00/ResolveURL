"""
    resolveurl XBMC Addon
    Copyright (C) 2015 tknorris

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
import json
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

class RPnetResolver(ResolveUrl):
    name = "RPnet"
    domains = ["*"]

    def __init__(self):
        self.net = common.Net()
        self.patterns = None
        self.hosts = None

    # ResolveUrl methods
    def get_media_url(self, host, media_id):
        username = self.get_setting('username')
        password = self.get_setting('password')
        url = 'https://premium.rpnet.biz/client_api.php'
        query = urllib.urlencode({'username': username, 'password': password, 'action': 'generate', 'links': media_id})
        url = url + '?' + query
        response = self.net.http_GET(url).content
        response = json.loads(response)
        if 'links' in response and response['links']:
            link = response['links'][0]
            if 'generated' in link:
                return link['generated']
            elif 'error' in link:
                raise ResolverError(link['error'])
        else:
            msg = 'No Link Returned'
            if 'error' in response and response['error']:
                msg += ': %s' % (response['error'][0])
            raise ResolverError(msg)

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'rpnet.biz', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
            patterns = []
            url = 'http://premium.rpnet.biz/hoster.json'
            response = self.net.http_GET(url).content
            hosters = json.loads(response)
            logger.log_debug('rpnet patterns: %s' % (hosters))
            patterns = [re.compile(pattern) for pattern in hosters['supported']]
        except Exception as e:
            logger.log_error('Error getting RPNet patterns: %s' % (e))
        return patterns

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        try:
            hosts = []
            url = 'http://premium.rpnet.biz/hoster2.json'
            response = self.net.http_GET(url).content
            hosts = json.loads(response)['supported']
            logger.log_debug('rpnet hosts: %s' % (hosts))
        except Exception as e:
            logger.log_error('Error getting RPNet hosts: %s' % (e))
        return hosts

    def valid_url(self, url, host):
        if url:
            if self.patterns is None:
                self.patterns = self.get_all_hosters()
                
            if any(pattern.search(url) for pattern in self.patterns):
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
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="%s" default=""/>' % (cls.__name__, i18n('username')))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('password')))
        return xml

    @classmethod
    def isUniversal(self):
        return True
