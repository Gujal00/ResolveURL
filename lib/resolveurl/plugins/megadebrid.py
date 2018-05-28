"""
    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0, JUL1EN094

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
import urllib
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

class MegaDebridResolver(ResolveUrl):
    name = "MegaDebrid"
    domains = ['*']
    profile_path = common.profile_path
    media_url = None

    def __init__(self):
        self.hosters = None
        self.token = None
        self.net = common.Net()
        scheme = 'https' if self.get_setting('use_https') == 'true' else 'http'
        self.base_url = '%s://www.mega-debrid.eu/api.php' % (scheme)
        self.headers = {'User-Agent': common.SMR_USER_AGENT}

    # ResolveUrl methods
    def get_media_url(self, host, media_id):
        common.logger.log('in get_media_url %s : %s' % (host, media_id))
        if self.token is None:
            raise ResolverError('No MD Token Available')
        
        url = self.base_url + '?' + urllib.urlencode({'action': 'getLink', 'token': self.token})
        data = {'link': media_id}
        html = self.net.http_POST(url, form_data=data, headers=self.headers).content
        js_data = json.loads(html)
        if js_data.get('response_code') == 'ok':
            if 'debridLink' in js_data:
                stream_url = js_data['debridLink'].strip('"')
                if stream_url.startswith('http'):
                    return stream_url
                else:
                    msg = 'MD Unusable Link: %s' % (stream_url)
            else:
                msg = 'MD No Link'
        else:
            msg = js_data.get('response_text', 'Unknown MD Error during resolve')
        
        logger.log_warning(msg)
        if isinstance(msg, unicode): msg = msg.encode('utf-8')
        raise ResolverError(msg)

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'mega-debrid.eu', url

    @common.cache.cache_method(cache_limit=8)
    def get_hosters(self):
        try:
            url = self.base_url + '?' + urllib.urlencode({'action': 'getHosters'})
            html = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(html)
            return [host.lower() for item in js_data['hosters'] for host in item]
        except Exception as e:
            logger.log_error('Error getting Meg-Debrid hosts: %s' % (e))
            return []

    def valid_url(self, url, host):
        if self.hosters is None:
            self.hosters = self.get_hosters()
            
        if url:
            match = re.search('//(.*?)/', url)
            if match:
                host = match.group(1)
            else:
                return False

        if host.startswith('www.'): host = host.replace('www.', '')
        logger.log_debug('in valid_url %s : %s' % (url, host))
        if host and any(host in item for item in self.hosters):
            return True

        return False

    # SiteAuth methods
    def login(self):
        try:
            common.logger.log('Mega-debrid - Logging In')
            username = self.get_setting('username')
            password = self.get_setting('password')
            if username and password:
                url = self.base_url + '?' + urllib.urlencode({'action': 'connectUser', 'login': username, 'password': password})
                html = self.net.http_GET(url, headers=self.headers).content
                js_data = json.loads(html)
                if js_data.get('response_code') == 'ok':
                    self.token = js_data['token']
                    return True
                else:
                    msg = js_data.get('response_text', 'Unknown Error')
            else:
                msg = 'No Username/Password'
        except Exception as e:
            msg = str(e)
        
        raise ResolverError('MD Login Failed: %s' % (msg))

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_use_https" type="bool" label="%s" default="true"/>' % (cls.__name__, i18n('use_https')))
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="%s" default=""/>' % (cls.__name__, i18n('username')))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('password')))
        return xml

    @classmethod
    def isUniversal(self):
        return True
