"""
    Plugin for ResolveURL
    Copyright (C) 2018 jsergio

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
from six.moves import urllib_parse, urllib_error
import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

CLIENT_ID = '522962560'
USER_AGENT = 'ResolveURL for Kodi/%s' % common.addon_version
FORMATS = common.VIDEO_FORMATS

base_url = 'https://www.premiumize.me'
api_path = '%s/api' % base_url
direct_dl_path = '%s/transfer/directdl' % api_path
list_folders_path = '%s/folder/list' % api_path
create_folder_path = '%s/folder/create' % api_path
delete_folder_path = '%s/folder/delete' % api_path
list_transfers_path = '%s/transfer/list' % api_path
create_transfer_path = '%s/transfer/create' % api_path
delete_transfer_path = '%s/transfer/delete' % api_path
clear_finished_path = '%s/transfer/clearfinished' % api_path
check_cache_path = '%s/cache/check' % api_path
list_services_path = '%s/services/list' % api_path
folder_name = 'resolveurl'
token_path = '%s/token' % base_url


# noinspection PyBroadException
class PremiumizeMeResolver(ResolveUrl):
    name = 'Premiumize.me'
    domains = ['*']
    media_url = None

    def __init__(self):
        self.hosts = []
        self.patterns = []
        self.net = common.Net()
        self.headers = {'User-Agent': USER_AGENT, 'Authorization': 'Bearer %s' % self.get_setting('token')}

    def get_media_url(self, host, media_id, cached_only=False, return_all=False):
        torrent = False
        cached = self.__check_cache(media_id)
        media_id_lc = media_id.lower()
        if cached:
            logger.log_debug('Premiumize.me: %s is readily available to stream' % media_id)
            if media_id_lc.endswith('.torrent') or media_id_lc.startswith('magnet:'):
                torrent = True
        elif media_id_lc.endswith('.torrent') or media_id_lc.startswith('magnet:'):
            if self.get_setting('cached_only') == 'true' or cached_only:
                raise ResolverError('Premiumize.me: {0}'.format(i18n('cached_torrents_only')))
            torrent = True
            logger.log_debug('Premiumize.me: initiating transfer to cloud for %s' % media_id)
            self.__initiate_transfer(media_id)
            if self.get_setting('clear_finished') == 'true':
                self.__clear_finished()
            # self.__delete_folder()

        link = self.__direct_dl(media_id, torrent=torrent, return_all=return_all)
        if link:
            if return_all:
                return link
            else:
                logger.log_debug('Premiumize.me: Resolved to %s' % link)
                return link + helpers.append_headers(self.headers)

        raise ResolverError('Link Not Found')

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'premiumize.me', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
            response = self.net.http_GET(list_services_path, headers=self.headers).content
            result = json.loads(response)
            aliases = result.get('aliases', {})
            patterns = result.get('regexpatterns', {})
            tldlist = []
            for tlds in list(aliases.values()):
                for tld in tlds:
                    tldlist.append(tld)
            if self.get_setting('torrents') == 'true':
                tldlist.extend([u'torrent', u'magnet'])
            regex_list = []
            for regexes in list(patterns.values()):
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
        if url and self.get_setting('torrents') == 'true':
            url_lc = url.lower()
            if url_lc.endswith('.torrent') or url_lc.startswith('magnet:'):
                return True

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

    def __check_cache(self, media_id):
        try:
            url = '%s?items[]=%s' % (check_cache_path, media_id)
            result = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(result)
            if 'status' in result:
                if result.get('status') == 'success':
                    response = result.get('response', False)
                    if isinstance(response, list):
                        return response[0]
        except:
            pass

        return False

    def __create_transfer(self, media_id):
        folder_id = self.__create_folder()
        if not folder_id == "":
            try:
                data = urllib_parse.urlencode({'src': media_id, 'folder_id': folder_id})
                response = self.net.http_POST(create_transfer_path, form_data=data, headers=self.headers).content
                result = json.loads(response)
                if 'status' in result:
                    if result.get('status') == 'success':
                        logger.log_debug('Transfer successfully started to the Premiumize.me cloud')
                        return result.get('id', "")
            except:
                pass

        return ""

    def __list_transfer(self, transfer_id):
        if not transfer_id == "":
            try:
                response = self.net.http_GET(list_transfers_path, headers=self.headers).content
                result = json.loads(response)
                if 'status' in result:
                    if result.get('status') == 'success':
                        for item in result.get("transfers"):
                            if item.get('id') == transfer_id:
                                return item
            except:
                pass

        return {}

    def __delete_transfer(self, transfer_id):
        if not transfer_id == "":
            try:
                data = urllib_parse.urlencode({'id': transfer_id})
                response = self.net.http_POST(delete_transfer_path, form_data=data, headers=self.headers).content
                result = json.loads(response)
                if 'status' in result:
                    if result.get('status') == 'success':
                        logger.log_debug('Transfer ID "%s" deleted from the Premiumize.me cloud' % transfer_id)
                        return True
            except:
                pass

        return False

    def __initiate_transfer(self, media_id, interval=5):
        transfer_id = self.__create_transfer(media_id)
        transfer_info = self.__list_transfer(transfer_id)
        if transfer_info:
            line1 = transfer_info.get('name')
            line2 = i18n('pm_save')
            line3 = transfer_info.get('message')
            with common.kodi.ProgressDialog(
                'ResolveURL Premiumize {0}'.format(i18n('transfer')),
                line1, line2, line3
            ) as pd:
                while not transfer_info.get('status') == 'seeding':
                    common.kodi.sleep(1000 * interval)
                    transfer_info = self.__list_transfer(transfer_id)
                    line1 = transfer_info.get('name')
                    line3 = transfer_info.get('message')
                    logger.log_debug(line3)
                    pd.update(int(float(transfer_info.get('progress')) * 100), line1=line1, line3=line3)
                    if pd.is_canceled():
                        keep_transfer = common.kodi.yesnoDialog(
                            heading='ResolveURL Premiumize {0}'.format(i18n('transfer')),
                            line1=i18n('pm_background')
                        )
                        if not keep_transfer:
                            self.__delete_transfer(transfer_id)
                        raise ResolverError('Transfer ID {0} :: {1}'.format(transfer_id, i18n('user_cancelled')))
                    elif transfer_info.get('status') == 'stalled':  # not sure on this value
                        self.__delete_transfer(transfer_id)
                        raise ResolverError('Transfer ID %s has stalled' % transfer_id)
            common.kodi.sleep(1000 * interval)  # allow api time to generate the stream_link

        return

    def __direct_dl(self, media_id, torrent=False, return_all=False):
        try:
            data = urllib_parse.urlencode({'src': media_id})
            response = self.net.http_POST(direct_dl_path, form_data=data, headers=self.headers).content
            result = json.loads(response)
            if 'status' in result:
                if result.get('status') == 'success':
                    if torrent:
                        if return_all:
                            sources = [{'name': link.get('path').split('/')[-1], 'link': link.get('link')}
                                       for link in result.get("content")
                                       if any(link.get('path').lower().endswith(x) for x in FORMATS)]
                            return sources
                        else:
                            _videos = [(int(item.get('size')), item.get('link'))
                                       for item in result.get("content")
                                       if any(item.get('path').lower().endswith(x) for x in FORMATS)]
                            try:
                                return max(_videos)[1]
                            except ValueError:
                                raise ResolverError('Failed to locate largest video file')
                    else:
                        return result.get('location', None)
                else:
                    raise ResolverError('Link Not Found: Error Code: %s' % result.get('status'))
            else:
                raise ResolverError('Unexpected Response Received')
        except:
            pass

        return None

    def __list_folders(self):
        try:
            response = self.net.http_GET(list_folders_path, headers=self.headers).content
            result = json.loads(response)
            if 'status' in result:
                if result.get('status') == 'success':
                    for items in result.get("content"):
                        if items.get('type') == 'folder' and items.get("name") == folder_name:
                            return items.get("id", "")
        except:
            pass

        return ""

    def __create_folder(self):
        folder_id = self.__list_folders()
        if folder_id == "":
            try:
                data = urllib_parse.urlencode({'name': folder_name})
                response = self.net.http_POST(create_folder_path, form_data=data, headers=self.headers).content
                result = json.loads(response)
                if 'status' in result:
                    if result.get('status') == 'success':
                        logger.log_debug('Folder named "%s" created on the Premiumize.me cloud' % folder_name)
                        return result.get('id', "")
            except:
                pass

            return ""
        else:
            return folder_id

    def __delete_folder(self):
        folder_id = self.__list_folders()
        if not folder_id == "":
            try:
                data = urllib_parse.urlencode({'id': folder_id})
                response = self.net.http_POST(delete_folder_path, form_data=data, headers=self.headers).content
                result = json.loads(response)
                if 'status' in result:
                    if result.get('status') == 'success':
                        logger.log_debug('Folder named "%s" deleted from the Premiumize.me cloud' % folder_name)
                        return True
            except:
                pass

        return False

    def __clear_finished(self):
        try:
            result = self.net.http_POST(clear_finished_path, form_data={}, headers=self.headers).content
            result = json.loads(result)
            if 'status' in result:
                if result.get('status') == 'success':
                    logger.log_debug('Finished transfers successfully cleared from the Premiumize.me cloud')
                    return True
        except:
            pass

        return False

    # SiteAuth methods
    def login(self):
        if not self.get_setting('token'):
            self.authorize_resolver()

    def authorize_resolver(self):
        data = {'response_type': 'device_code', 'client_id': CLIENT_ID}
        js_result = json.loads(self.net.http_POST(token_path, form_data=data, headers=self.headers).content)
        line1 = '{0}: {1}'.format(i18n('goto_url'), js_result.get('verification_uri'))
        line2 = '{0}: {1}'.format(i18n('enter_prompt'), js_result.get('user_code'))
        with common.kodi.CountdownDialog(
            'Resolve URL Premiumize {0}'.format(i18n('authorisation')), line1, line2,
            countdown=180, interval=js_result.get('interval', 5)
        ) as cd:
            result = cd.start(self.__get_token, [js_result.get('device_code')])

        # cancelled
        if result is None:
            return
        return result

    def __get_token(self, device_code):
        try:
            data = {'grant_type': 'device_code', 'client_id': CLIENT_ID, 'code': device_code}
            logger.log_debug('Authorizing Premiumize.me: %s' % CLIENT_ID)
            js_result = json.loads(self.net.http_POST(token_path, form_data=data, headers=self.headers).content)
            logger.log_debug('Authorizing Premiumize.me Result: |%s|' % js_result)
            self.set_setting('token', js_result['access_token'])
        except urllib_error.HTTPError as e:
            try:
                js_result = json.loads(e.read())
                if 'error' in js_result:
                    msg = js_result.get('error')
                else:
                    msg = 'Unknown Error (1)'
            except:
                msg = 'Unknown Error (2)'
            logger.log_debug('Premiumize.me Authorization Failed: %s' % msg)
            return False
        except Exception as e:
            logger.log_debug('Exception during PM auth: %s' % e)
            return False
        else:
            return True

    def reset_authorization(self):
        self.set_setting('token', '')

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_torrents" type="bool" label="%s" default="true"/>' % (cls.__name__, i18n('torrents')))
        xml.append('<setting id="%s_cached_only" enable="eq(-1,true)" type="bool" label="%s" default="false" />' % (cls.__name__, i18n('cached_only')))
        xml.append('<setting id="%s_clear_finished" enable="eq(-2,true)" type="bool" label="%s" default="false" />' % (cls.__name__, i18n('clear_finished')))
        xml.append('<setting id="%s_auth" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_pm)"/>' % (cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="%s_reset" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_pm)"/>' % (cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="%s_token" visible="false" type="text" default=""/>' % cls.__name__)
        return xml

    @classmethod
    def isUniversal(cls):
        return True
