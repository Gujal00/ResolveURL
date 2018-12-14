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
import urllib
import json
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

USER_AGENT = 'ResolveURL for Kodi/%s' % common.addon_version


class PremiumizeMeResolver(ResolveUrl):
    name = "Premiumize.me"
    domains = ["*"]
    media_url = None

    def __init__(self):
        self.hosts = []
        self.patterns = []
        self.net = common.Net()
        self.password = self.get_setting('password')
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id):
        cached = self.__check_cache(media_id)
        if cached:
            logger.log_debug('Premiumize.me: %s is readily available to stream' % media_id)
        url = 'https://www.premiumize.me/api/transfer/directdl?apikey=%s' % self.password
        data = urllib.urlencode({'src': media_id})
        response = self.net.http_POST(url, form_data=data, headers=self.headers).content
        result = json.loads(response)
        if 'status' in result:
            if result.get('status') == 'success':
                link = result.get('location')
            else:
                raise ResolverError('Link Not Found: Error Code: %s' % result.get('status'))
        else:
            raise ResolverError('Unexpected Response Received')

        logger.log_debug('Premiumize.me: Resolved to %s' % link)
        return link + helpers.append_headers(self.headers)

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'premiumize.me', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
            url = 'https://www.premiumize.me/api/services/list?apikey=%s' % self.password
            response = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(response)
            aliases = result.get('aliases', {})
            patterns = result.get('regexpatterns', {})
            tldlist = []
            for tlds in aliases.values():
                for tld in tlds:
                    tldlist.append(tld)
            regex_list = []
            for regexes in patterns.values():
                for regex in regexes:
                    try:
                        regex_list.append(re.compile(regex))
                    except:
                        common.logger.log_warning('Throwing out bad Premiumize regex: %s' % regex)
            logger.log_debug('Premiumize.me patterns: %s regex: (%d) hosts: %s' % (patterns, len(regex_list), tldlist))
            return tldlist, regex_list
        except Exception as e:
            logger.log_error('Error getting Premiumize hosts: %s' % e)
        return [], []

    def valid_url(self, url, host):
        if not self.patterns or not self.hosts:
            self.hosts, self.patterns = self.get_all_hosters()

        if url:
            if not url.endswith('/'):
                url += '/'
            for pattern in self.patterns:
                if pattern.findall(url):
                    return True
        elif host:
            if host.startswith('www.'):
                host = host.replace('www.', '')
            if any(host in item for item in self.hosts):
                return True

        return False

    def __check_cache(self, item):
        try:
            url = 'https://www.premiumize.me/api/cache/check?apikey=%s&items[]=%s' % (self.password, item)
            result = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(result)
            if 'status' in result:
                if result.get('status') == 'success':
                    response = result.get('response', False)
                    if isinstance(response, list):
                        return response[0]
            return False
        except:
            return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_password" enable="eq(-1,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('api_key')))
        return xml

    @classmethod
    def isUniversal(cls):
        return True
