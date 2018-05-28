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

import re
import json
import hashlib
import time
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

class DebridLinkResolver(ResolveUrl):
    name = "Debrid-Link.fr"
    domains = ["*"]
    media_url = None

    def __init__(self):
        self.net = common.Net()
        self.base_url = 'https://debrid-link.fr/api'
        self.hosts = None

    def get_media_url(self, host, media_id):
        offset = self.get_setting('ts_offset')
        token = self.get_setting('token')
        api_key = self.get_setting('key')
        if not offset or not token or not api_key:
            logger.log_debug('offset: %s, token: %s, key: %s' % (offset, token, api_key))
            raise ResolverError('Insufficent Information to make API call')
        
        url = '/downloader/add'
        server_ts = int(time.time()) - int(offset)
        signature = hashlib.sha1(str(server_ts) + url + api_key).hexdigest()
        url = self.base_url + url
        headers = {'X-DL-SIGN': signature, 'X-DL-TOKEN': token, 'X-DL-TS': server_ts}
        logger.log_debug('Debrid-Link Headers: %s' % (headers))
        js_data = self.net.http_POST(url, form_data={'link': media_id}, headers=headers).content
        js_data = json.loads(js_data)
        self.__store_offset(js_data)
        if js_data.get('result') == 'OK':
            stream_url = js_data.get('value', {}).get('downloadLink')
            if stream_url is None:
                raise ResolverError('No usable link returned from Debrid-Link.fr')
            
            logger.log_debug('Debrid-Link.fr Resolved to %s' % (stream_url))
            return stream_url
        else:
            raise ResolverError('Debrid-Link.fr Link failed: %s' % (js_data.get('ERR', '')))

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'debrid-link.fr', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
            url = self.base_url + '/downloader/status'
            js_data = self.net.http_GET(url).content
            js_data = json.loads(js_data)
            self.__store_offset(js_data)
            host_list = js_data.get('value', {}).get('hosters', [])
            hosts = [host for status in host_list for host in status.get('hosts', [])]
            return hosts
        except Exception as e:
            logger.log_error('Error getting debrid-link hosts: %s' % (e))
        return []

    def __store_offset(self, js_data):
        if 'ts' in js_data:
            offset = int(time.time()) - js_data['ts']
            self.set_setting('ts_offset', offset)
        
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

    def login(self):
        url = self.base_url + '/account/login'
        username = self.get_setting('username')
        password = self.get_setting('password')
        login_data = {'pseudo': username, 'password': password}
        js_data = self.net.http_POST(url, form_data=login_data).content
        js_data = json.loads(js_data)
        if js_data.get('result') == 'OK':
            self.__store_offset(js_data)
            if 'value' in js_data:
                self.set_setting('token', js_data['value'].get('token'))
                self.set_setting('key', js_data['value'].get('key'))
            return True

        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="%s" default=""/>' % (cls.__name__, i18n('username')))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('password')))
        xml.append('<setting id="%s_ts_offset" type="number" visible="false" enable="false" default="0"/>' % (cls.__name__))
        xml.append('<setting id="%s_token" type="text" visible="false" enable="false"/>' % (cls.__name__))
        xml.append('<setting id="%s_key" type="text" visible="false" enable="false"/>' % (cls.__name__))
        return xml

    @classmethod
    def isUniversal(self):
        return True
