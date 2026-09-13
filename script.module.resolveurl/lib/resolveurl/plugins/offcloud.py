"""
    Plugin for ResolveURL
    Copyright (c) 2026 gujal

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

AGENT = 'ResolveURL'
VERSION = common.addon_version
USER_AGENT = '{0}/{1}'.format(AGENT, VERSION)
FORMATS = common.VIDEO_FORMATS

DOMAIN = 'https://offcloud.com/'
auth_api = DOMAIN + 'oauth'
api = DOMAIN + 'api'


class OffCloudResolver(ResolveUrl):
    name = 'OffCloud'
    domains = ['*']

    def __init__(self):
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}
        if self.get_setting('apikey'):
            self.headers.update({'Authorization': 'Bearer ' + self.get_setting('apikey')})

    def get_media_url(self, host, media_id, cached_only=False, return_all=False):
        if media_id.lower().startswith('magnet:'):
            r = re.search(r'''(magnet:\?xt=urn:btih:[a-f0-9]+)''', media_id, re.I)
            if r:
                _hash = r.group(1)
                cached = self.__check_cache(_hash)
                if cached:
                    transfer_info = self.__browse_magnet(_hash)
                    if return_all:
                        sources = [
                            {'name': link.get('filename'), 'link': link.get('url')}
                            for link in transfer_info
                            if any(link.get('filename').lower().endswith(x) for x in FORMATS)
                        ]
                        return sources
                    else:
                        sources = [
                            (link.get('size'), link.get('url'))
                            for link in transfer_info
                            if any(link.get('filename').lower().endswith(x) for x in FORMATS)
                        ]
                        return max(sources)[1]
                else:
                    if cached_only or self.get_setting('cached_only') == 'true':
                        raise ResolverError('OffCloud: {0}'.format(i18n('cached_torrents_only')))

                    ok, req_id = self.__create_transfer(_hash)
                    if not ok:
                        raise ResolverError('OffCloud: {0}'.format(i18n('no_stream')))

                transfer_info = self.__explore_transfer(req_id, info='detailed')
                self.__remove_transfer(req_id)
                if return_all:
                    sources = [
                        {'name': link.get('name'), 'link': link.get('url')}
                        for link in transfer_info
                        if any(link.get('name').lower().endswith(x) for x in FORMATS)
                    ]
                    return sources
                else:
                    sources = [
                        (link.get('size'), link.get('url'))
                        for link in transfer_info
                        if any(link.get('name').lower().endswith(x) for x in FORMATS)
                    ]
                    return max(sources)[1]

        ok, req_id = self.__create_transfer(media_id)
        if not ok:
            raise ResolverError('OffCloud: {0}'.format(i18n('no_stream')))

        res = self.__explore_transfer(req_id)
        if res:
            self.__remove_transfer(req_id)
            return res[0]

        raise ResolverError('OffCloud: {0}'.format(i18n('no_stream')))

    def __check_cache(self, magnet_hash):
        try:
            data = {'urls': [magnet_hash]}
            url = api + '/cache/info'
            result = self.net.http_POST(url, headers=self.headers, form_data=data, jdata=True).json
            if result:
                return result[0].get('cached')
        except:
            pass

        return False

    def __browse_magnet(self, magnet_hash):
        data = {'url': magnet_hash}
        url = api + '/cache/download'
        result = self.net.http_POST(url, headers=self.headers, form_data=data, jdata=True).json
        return result

    def __create_transfer(self, furl):
        data = {'url': furl}
        url = api + '/cloud'
        result = self.net.http_POST(url, headers=self.headers, form_data=data, jdata=True).json
        if result.get('requestId'):
            request_id = result.get('requestId')
            logger.log_debug('Transfer successfully started to the OffCloud cloud')
            return self.__initiate_transfer(request_id), request_id
        else:
            raise ResolverError(result.get('status'))

    def __initiate_transfer(self, request_id, interval=5):
        transfer_info = self.__list_transfer(request_id)
        if transfer_info:
            if transfer_info.get('status') != 'downloaded':
                line1 = transfer_info.get('fileName')
                line2 = i18n('oc_save')
                line3 = transfer_info.get('message')
                with common.kodi.ProgressDialog('ResolveURL OffCloud {0}'.format(i18n('transfer')), line1, line2, line3) as pd:
                    while not transfer_info.get('status') == 'downloaded':
                        common.kodi.sleep(1000 * interval)
                        transfer_info = self.__list_transfer(request_id)
                        if transfer_info.get('status') != 'downloaded':
                            line1 = transfer_info.get('fileName')
                            progress = int(transfer_info.get('progress') * 100)
                            line3 = transfer_info.get('message')
                            logger.log_debug(line3)
                            pd.update(progress, line1=line1, line3=line3)
                            if pd.is_canceled():
                                keep_transfer = common.kodi.yesnoDialog(
                                    heading='ResolveURL OffCloud {0}'.format(i18n('transfer')),
                                    line1=i18n('oc_background')
                                )
                                if not keep_transfer:
                                    self.__remove_transfer(request_id)
                                logger.log_debug('ResolveURL OffCloud {0} ID {1} :: {2}'.format(i18n('transfer'), request_id, i18n('user_cancelled')))
                                return False
            return True
        else:
            self.__remove_transfer(request_id)
            raise ResolverError('OffCloud Magnet {0} :: {1}'.format(request_id, transfer_info))

    def __list_transfer(self, request_id):
        data = {'requestId': request_id}
        url = api + '/cloud/status'
        res = self.net.http_POST(url, headers=self.headers, form_data=data, jdata=True).json
        return res.get('status')

    def __remove_transfer(self, request_id):
        data = {'requests': [request_id]}
        url = api + '/cloud/remove'
        result = self.net.http_POST(url, headers=self.headers, form_data=data, jdata=True).json
        if result.get('success'):
            logger.log_debug('Request "{0}" deleted from OffCloud'.format(request_id))
            return True
        return False

    def __explore_transfer(self, request_id, info=''):
        url = api + '/cloud/explore/' + request_id
        if info:
            url += '?format={0}'.format(info)
        resp = self.net.http_GET(url, headers=self.headers).json
        if resp:
            if info == 'detailed':
                return resp.get('files')
            return resp

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'offcloud.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        url = api + '/sites'
        try:
            js_data = self.net.http_GET(url, headers=self.headers).json
            hosts = [x.get('name') for x in js_data if x.get('status') == 'up']
            if self.get_setting('torrents') == 'true':
                hosts.extend(['torrent', 'magnet'])
            logger.log_debug('OffCloud hosts : {0}'.format(hosts))
        except Exception as e:
            logger.log_error('Error getting OC Hosts: {0}'.format(e))
        return hosts

    def valid_url(self, url, host):
        logger.log_debug('in valid_url {0} : {1}'.format(url, host))
        if url:
            if url.lower().startswith('magnet:') and self.get_setting('torrents') == 'true':
                return True
            host = urllib_parse.urlsplit(url).netloc

        if self.hosts is None:
            self.hosts = self.get_hosts()

        if any(item.lower() in host.lower() for item in self.hosts):
            return True

        return False

    # SiteAuth methods
    def login(self):
        if not self.get_setting('apikey'):
            self.authorize_resolver()

    def reset_authorization(self):
        if 'Authorization' in self.headers.keys():
            self.headers.pop('Authorization')
        self.set_setting('apikey', '')
        self.set_setting('user', '')

    def authorize_resolver(self):
        url = auth_api + '/device/code'
        js_data = self.net.http_POST(url, headers=self.headers, form_data={}, jdata=True).json
        line1 = '{0}: {1}'.format(i18n('goto_url'), js_data.get('verification_uri'))
        line2 = '{0}: {1}'.format(i18n('enter_prompt'), js_data.get('user_code'))
        qr_file = common.make_qr_file(js_data.get('verification_uri_complete'))
        with common.kodi.AuthProgressDialog(
            'ResolveUrl OffCloud {0}'.format(i18n('authorisation')), line1, line2,
            image=qr_file, countdown=js_data.get('expires_in', 300)
        ) as cd:
            result = cd.start(self.__check_auth, [js_data.get('device_code')])

        # cancelled
        if result is None:
            return
        return self.__get_token(js_data.get('device_code'))

    def __get_token(self, token):
        api_key = self.get_setting('apikey')
        logger.log_debug('Authorizing OffCloud Result: |{0}|'.format(api_key))
        self.headers.update({'Authorization': 'Bearer ' + api_key})
        url = api + '/account/info'
        js_data = self.net.http_GET(url, headers=self.headers).json
        user = js_data.get('email')
        if user:
            self.set_setting('user', user)
            return True

    def __check_auth(self, token):
        activated = False
        url = auth_api + '/token'
        params = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': token
        }
        try:
            js_data = self.net.http_POST(url, headers=self.headers, form_data=params, jdata=True).json
            if js_data:
                activated = 'access_token' in list(js_data.keys())
                if activated:
                    self.set_setting('apikey', js_data.get('access_token'))
        except Exception as e:
            logger.log_debug('Exception during OC auth: {0}'.format(e))
        return activated

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="{0}_torrents" type="bool" label="{1}" default="true"/>'.format(cls.__name__, i18n('torrents')))
        xml.append('<setting id="{0}_cached_only" enable="eq(-1,true)" type="bool" label="{1}" default="false" />'.format(cls.__name__, i18n('cached_only')))
        xml.append('<setting id="{0}_auth" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_oc)"/>'.format(cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="{0}_reset" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_oc)"/>'.format(cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="{0}_user" enable="false" label="{1}" visible="eq(-4,true)" type="text" default=""/>'.format(cls.__name__, i18n('username')))
        xml.append('<setting id="{0}_apikey" visible="false" type="text" default=""/>'.format(cls.__name__))
        return xml

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('apikey')

    @classmethod
    def isUniversal(cls):
        return True
