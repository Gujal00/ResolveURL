"""
    Plugin for ResolveURL
    Copyright (c) 2020 gujal

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
from six.moves import urllib_parse, urllib_error
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

CLIENT_ID = 'TH7yOa_pgRD1MRyIs6496Q'
USER_AGENT = 'ResolveURL for Kodi/{0}'.format(common.addon_version)
FORMATS = common.VIDEO_FORMATS

api_url = 'https://debrid-link.fr/api/v2'


class DebridLinkResolver(ResolveUrl):
    name = 'Debrid-Link'
    domains = ['*']

    def __init__(self):
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT, 'Authorization': 'Bearer {0}'.format(self.get_setting('token'))}

    def get_media_url(self, host, media_id, retry=False, cached_only=False, return_all=False):
        try:
            if media_id.lower().startswith('magnet:') or '.torrent' in media_id.lower():
                if self.__check_cache(media_id):
                    logger.log_debug('Debrid-Link: BTIH {0} is readily available to stream'.format(media_id))
                    transfer_id = self.__create_transfer(media_id)
                else:
                    if self.get_setting('cached_only') == 'true' or cached_only:
                        raise ResolverError('Debrid-Link: {0}'.format(i18n('cached_torrents_only')))
                    else:
                        transfer_id = self.__create_transfer(media_id)
                        if transfer_id:
                            self.__initiate_transfer(transfer_id)
                        else:
                            raise ResolverError('Debrid-Link {0}'.format(i18n('queue_fail')))

                if transfer_id:
                    transfer_info = self.__list_transfer(transfer_id)
                    if return_all:
                        sources = [{'name': link.get('name').split('/')[-1], 'link': link.get('downloadUrl')}
                                   for link in transfer_info.get('files')
                                   if any(link.get('name').lower().endswith(x) for x in FORMATS)]
                        return sources
                    sources = [(item.get('size'), item.get('downloadUrl'))
                               for item in transfer_info.get('files')
                               if any(item.get('name').lower().endswith(x) for x in FORMATS)]
                    stream_url = max(sources)[1]
                    return stream_url
                else:
                    raise ResolverError('Debrid-Link {0}'.format(i18n('no_torrents')))

            url = '{0}/downloader/add'.format(api_url)
            data = {'url': media_id}
            js_data = json.loads(self.net.http_POST(url, form_data=data, headers=self.headers).content)
        except urllib_error.HTTPError as e:
            if not retry and e.code == 401:
                if self.get_setting('refresh'):
                    self.refresh_token()
                    return self.get_media_url(host, media_id, retry=True)
                else:
                    self.reset_authorization()
                    raise ResolverError('Debrid-Link {0}'.format(i18n('auth_fail')))
            else:
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = js_result.get('error')
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise ResolverError('Debrid-Link Error: {0} ({1})'.format(msg, e.code))
        except Exception as e:
            raise ResolverError('Debrid-Link Error: {0}'.format(e))
        else:
            if js_data.get('success', False):
                stream_url = js_data.get('value', {}).get('downloadUrl')
                if stream_url is None:
                    raise ResolverError(i18n('no_usable'))

                logger.log_debug('Debrid-Link Resolved to {0}'.format(stream_url))
                return stream_url
            else:
                raise ResolverError('Debrid-Link Error: {0}'.format(js_data.get('ERR', '')))

        raise ResolverError(i18n('no_usable'))

    def __check_cache(self, media_id, retry=False):
        if media_id.startswith('magnet:'):
            media_id = re.findall('''magnet:.+?urn:[a-zA-Z0-9]+:([a-zA-Z0-9]+)''', media_id.lower(), re.I)[0]
        else:
            media_id = urllib_parse.quote_plus(media_id)
        try:
            url = '{0}/seedbox/cached?url={1}'.format(api_url, media_id)
            result = json.loads(self.net.http_GET(url, headers=self.headers).content)
            if result.get('success', False):
                if isinstance(result.get('value'), dict):
                    if media_id in list(result.get('value').keys()):
                        return True
        except urllib_error.HTTPError as e:
            if not retry and e.code == 401:
                if self.get_setting('refresh'):
                    self.refresh_token()
                    return self.__check_cache(media_id, retry=True)
                else:
                    self.reset_authorization()
                    raise ResolverError(i18n('auth_fail'))
            else:
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = js_result.get('error')
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise ResolverError('Debrid-Link Error: {0} ({1})'.format(msg, e.code))
        except Exception as e:
            if "'list' object" not in e:
                raise ResolverError('Debrid-Link Error: {0}'.format(e))

        return False

    def __list_transfer(self, transfer_id):
        try:
            url = '{0}/seedbox/{1}/infos'.format(api_url, transfer_id)
            js_data = json.loads(self.net.http_GET(url, headers=self.headers).content)
            if js_data.get('success', False):
                return js_data.get('value')
        except:
            pass

        return {}

    def __create_transfer(self, media_id):
        try:
            url = '{0}/seedbox/add'.format(api_url)
            data = {'url': media_id,
                    'async': 'true'}
            js_result = json.loads(self.net.http_POST(url, form_data=data, headers=self.headers).content)
            if js_result.get('value'):
                logger.log_debug('Transfer successfully started to the Debrid-Link cloud')
                return js_result.get('value').get('id')
        except:
            pass

        return ""

    def __initiate_transfer(self, transfer_id, interval=5):
        try:
            transfer_info = self.__list_transfer(transfer_id)
            if transfer_info:
                line1 = transfer_info.get('name')
                line2 = i18n('dl_save')
                line3 = transfer_info.get('serverId')
                with common.kodi.ProgressDialog(
                    'ResolveURL Debrid-Link {0}'.format(i18n('transfer')),
                    line1, line2, line3
                ) as pd:
                    while transfer_info.get('downloadPercent') < 100.0:
                        common.kodi.sleep(1000 * interval)
                        transfer_info = self.__list_transfer(transfer_id)
                        file_size = round(float(transfer_info.get('totalSize')) / (1000**3), 2)
                        if transfer_info.get('status') == 4:
                            download_speed = round(float(transfer_info.get('downloadSpeed')) / (1000**2), 2)
                            progress = int(transfer_info.get('downloadPercent'))
                            line3 = "{0} {1}MB/s from {2} peers, {3}% {4} {5}GB {6}".format(
                                i18n('downloading'), download_speed, transfer_info.get('peersConnected'), progress,
                                i18n('of'), file_size, i18n('completed')
                            )
                        elif transfer_info.get('status') == 6:
                            upload_speed = round(float(transfer_info.get('uploadSpeed')) / (1000**2), 2)
                            progress = int(transfer_info.get('downloadPercent'))
                            line3 = "{0} {1}MB/s to {2} peers, {3}% {4} {5} {6} GB".format(
                                i18n('uploading'), upload_speed, transfer_info.get('peersConnected'),
                                progress, i18n('completed'), i18n('of'), file_size
                            )
                        else:
                            line3 = transfer_info.get('serverId')
                            progress = 0
                        logger.log_debug(line3)
                        pd.update(progress, line3=line3)
                        if pd.is_canceled():
                            keep_transfer = common.kodi.yesnoDialog(
                                heading='ResolveURL Debrid-Link {0}'.format(i18n('transfer')),
                                line1=i18n('dl_background')
                            )
                            if not keep_transfer:
                                self.__delete_transfer(transfer_id)
                            raise ResolverError('Transfer ID {0} :: {1}'.format(transfer_id, i18n('user_cancelled')))
            return

        except Exception as e:
            self.__delete_transfer(transfer_id)
            raise ResolverError('Transfer ID {0} :: {1}'.format(transfer_id, e))

    def __delete_transfer(self, transfer_id):
        try:
            url = '{0}/seedbox/{1}/remove'.format(api_url, transfer_id)
            js_data = json.loads(self.net.http_DELETE(url, headers=self.headers).content)
            if js_data.get('success', False):
                if transfer_id in js_data.get('value'):
                    logger.log_debug('Transfer ID "{0}" deleted from Debrid-Link cloud'.format(transfer_id))
                    return True
        except:
            pass

        return False

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'debrid-link.fr', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self, retry=False):
        hosters = []
        url = '{0}/downloader/regex'.format(api_url)
        try:
            js_data = json.loads(self.net.http_GET(url, headers=self.headers).content)
            if js_data.get('success', False):
                js_data = js_data.get('value')
                regexes = [value.get('regexs')[0] for value in js_data]
                logger.log_debug('Debrid-Link regexes : {0}'.format(len(regexes)))
                for regex in regexes:
                    try:
                        hosters.append(re.compile(regex))
                    except:
                        pass
                logger.log_debug('Debrid-Link hosters : {0}'.format(len(hosters)))
            else:
                logger.log_error('Error getting DL Hosters')
        except urllib_error.HTTPError as e:
            if not retry and e.code == 401:
                if self.get_setting('refresh'):
                    self.refresh_token()
                    return self.get_all_hosters(retry=True)
                else:
                    self.reset_authorization()
                    raise ResolverError(i18n('auth_fail'))
            else:
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = js_result.get('error')
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise ResolverError('Debrid-Link Error: {0} ({1})'.format(msg, e.code))
        except Exception as e:
            logger.log_error('Error getting DL Hosters: {0}'.format(e))
        return hosters

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        url = '{0}/downloader/hostnames'.format(api_url)
        try:
            js_data = json.loads(self.net.http_GET(url, headers=self.headers).content)
            if js_data.get('success', False):
                hosts = js_data.get('value')
                if self.get_setting('torrents') == 'true':
                    hosts.extend(['torrent', 'magnet'])
                logger.log_debug('Debrid-Link hosts : {0}'.format(hosts))
            else:
                logger.log_error('Error getting DL Hosts')
        except Exception as e:
            logger.log_error('Error getting DL Hosts: {0}'.format(e))
        return hosts

    def valid_url(self, url, host):
        logger.log_debug('in valid_url {0} : {1}'.format(url, host))
        if url:
            if (url.lower().startswith('magnet:') or '.torrent' in url.lower()) and self.get_setting('torrents') == 'true':
                return True

            if self.hosters is None:
                self.hosters = self.get_all_hosters()

            for regexp in self.hosters:
                if re.search(regexp, url):
                    logger.log_debug('Debrid-Link Match found')
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

    def refresh_token(self):
        REFRESH_TOKEN = self.get_setting('refresh')
        logger.log_debug('Refreshing Expired Debrid-Link Token: |{0}|'.format(REFRESH_TOKEN))
        try:
            url = '{0}/oauth/token'.format(api_url[:-3])
            data = {'client_id': CLIENT_ID,
                    'refresh_token': REFRESH_TOKEN,
                    'grant_type': 'refresh_token'}
            if self.headers.get('Authorization', False):
                self.headers.pop('Authorization')
            js_result = json.loads(self.net.http_POST(url, form_data=data, headers=self.headers).content)
            if js_result.get('access_token', False):
                self.set_setting('token', js_result.get('access_token'))
                self.headers.update({'Authorization': 'Bearer {0}'.format(js_result.get('access_token'))})
                return True
            else:
                # empty all auth settings to force a re-auth on next use
                self.reset_authorization()
                raise ResolverError('Unable to Refresh Debrid-Link Token')
        except urllib_error.HTTPError as e:
            if e.code == 400:
                js_data = json.loads(e.read())
                if js_data.get('error') == 'invalid_request':
                    logger.log_debug('Exception during DL auth: {0}'.format(js_data.get('error')))
                    # empty all auth settings to force a re-auth on next use
                    self.reset_authorization()
                    raise ResolverError(i18n('auth_fail'))
            else:
                logger.log_debug('Exception during DL auth: {0}'.format(e))
                raise ResolverError(i18n('auth_fail'))
        except Exception as e:
            self.reset_authorization()
            logger.log_debug('Debrid-Link Authorization Failed: {0}'.format(e))
            return False

    def authorize_resolver(self):
        url = '{0}/oauth/device/code'.format(api_url[:-3])
        data = {'client_id': CLIENT_ID,
                'scope': 'get.post.delete.downloader get.post.delete.seedbox get.account'}
        if self.headers.get('Authorization', False):
            self.headers.pop('Authorization')
        js_result = json.loads(self.net.http_POST(url, form_data=data, headers=self.headers).content)
        line1 = '{0}: {1}'.format(i18n('goto_url'), js_result.get('verification_url'))
        line2 = '{0}: {1}'.format(i18n('enter_prompt'), js_result.get('user_code'))
        with common.kodi.CountdownDialog(
            'ResolveURL Debrid-Link {0}'.format(i18n('authorisation')), line1, line2,
            countdown=js_result.get('expires_in'), interval=10
        ) as cd:
            result = cd.start(self.__check_auth, [js_result.get('device_code')])

        # cancelled
        if result is None:
            return
        return True

    def __check_auth(self, device_code):
        activated = False
        try:
            url = '{0}/oauth/token'.format(api_url[:-3])
            data = {'client_id': CLIENT_ID,
                    'code': device_code,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'}
            if self.headers.get('Authorization', False):
                self.headers.pop('Authorization')
            js_data = json.loads(self.net.http_POST(url, form_data=data, headers=self.headers).content)
            if js_data.get('access_token', False):
                logger.log_debug('Authorizing Debrid-Link Result: |{0}|'.format(js_data))
                activated = True
                self.set_setting('token', js_data.get('access_token'))
                self.set_setting('client_id', CLIENT_ID)
                self.set_setting('refresh', js_data.get('refresh_token'))
        except urllib_error.HTTPError as e:
            if e.code == 400:
                js_data = json.loads(e.read())
                if js_data.get('error') != 'authorization_pending':
                    logger.log_debug('Exception during DL auth: {0}'.format(e))
                    raise ResolverError(i18n('auth_fail'))
            else:
                logger.log_debug('Exception during DL auth: {0}'.format(e))
                raise ResolverError(i18n('auth_fail'))
        except Exception as e:
            logger.log_debug('Exception during DL auth: {0}'.format(e))
        return activated

    def reset_authorization(self):
        self.set_setting('token', '')
        self.set_setting('refresh', '')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="{0}_torrents" type="bool" label="{1}" default="true"/>'.format(cls.__name__, i18n('torrents')))
        xml.append('<setting id="{0}_cached_only" enable="eq(-1,true)" type="bool" label="{1}" default="false" />'.format(cls.__name__, i18n('cached_only')))
        xml.append('<setting id="{0}_auth" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_dl)"/>'.format(cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="{0}_reset" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_dl)"/>'.format(cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="{0}_token" visible="false" type="text" default=""/>'.format(cls.__name__))
        xml.append('<setting id="{0}_refresh" visible="false" type="text" default=""/>'.format(cls.__name__))
        xml.append('<setting id="{0}_client_id" visible="false" type="text" default=""/>'.format(cls.__name__))
        return xml

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    @classmethod
    def isUniversal(cls):
        return True
