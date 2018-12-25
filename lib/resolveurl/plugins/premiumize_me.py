"""
    resolveurl XBMC Addon
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
import urllib
import json
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

USER_AGENT = 'ResolveURL for Kodi/%s' % common.addon_version

base_url = 'https://www.premiumize.me/api'
direct_dl_path = 'transfer/directdl'
list_folders_path = 'folder/list'
create_folder_path = 'folder/create'
delete_folder_path = 'folder/delete'
list_transfers_path = 'transfer/list'
create_transfer_path = 'transfer/create'
delete_transfer_path = 'transfer/delete'
clear_finished_path = 'transfer/clearfinished'
check_cache_path = 'cache/check'
list_services_path = 'services/list'
folder_name = 'resolveurl'


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
        torrent = False
        cached = self.__check_cache(media_id)
        media_id_lc = media_id.lower()
        if cached:
            logger.log_debug('Premiumize.me: %s is readily available to stream' % media_id)
            if media_id_lc.endswith('.torrent') or media_id_lc.startswith('magnet:'):
                torrent = True
        elif media_id_lc.endswith('.torrent') or media_id_lc.startswith('magnet:'):
            torrent = True
            logger.log_debug('Premiumize.me: initiating transfer to cloud for %s' % media_id)
            self.__initiate_transfer(media_id)
            self.__clear_finished()
            # self.__delete_folder()

        link = self.__direct_dl(media_id, torrent=torrent)
        if not link == "":
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
            url = '%s/%s?apikey=%s' % (base_url, list_services_path, self.password)
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

    def __check_cache(self, item):
        try:
            url = '%s/%s?apikey=%s&items[]=%s' % (base_url, check_cache_path, self.password, item)
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
                url = '%s/%s?apikey=%s' % (base_url, create_transfer_path, self.password)
                data = urllib.urlencode({'src': media_id, 'folder_id': folder_id})
                response = self.net.http_POST(url, form_data=data, headers=self.headers).content
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
                url = '%s/%s?apikey=%s' % (base_url, list_transfers_path, self.password)
                response = self.net.http_GET(url, headers=self.headers).content
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
                url = '%s/%s?apikey=%s' % (base_url, delete_transfer_path, self.password)
                data = urllib.urlencode({'id': transfer_id})
                response = self.net.http_POST(url, form_data=data, headers=self.headers).content
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
            line2 = 'Saving torrent to the Premiumize Cloud'
            line3 = transfer_info.get('message')
            with common.kodi.ProgressDialog('Resolve URL Premiumize Transfer', line1, line2, line3) as pd:
                while not transfer_info.get('status') == 'seeding':
                    common.kodi.sleep(1000 * interval)
                    transfer_info = self.__list_transfer(transfer_id)
                    line1 = transfer_info.get('name')
                    line3 = transfer_info.get('message')
                    logger.log_debug(line3)
                    pd.update(int(float(transfer_info.get('progress')) * 100), line1=line1, line3=line3)
                    if pd.is_canceled():
                        self.__delete_transfer(transfer_id)
                        # self.__delete_folder()
                        raise ResolverError('Transfer ID %s canceled by user' % transfer_id)
                    elif transfer_info.get('status') == 'stalled':  # not sure on this value
                        self.__delete_transfer(transfer_id)
                        # self.__delete_folder()
                        raise ResolverError('Transfer ID %s has stalled' % transfer_id)
            common.kodi.sleep(1000 * interval)  # allow api time to generate the stream_link
        self.__delete_transfer(transfer_id)  # just in case __clear_finished() doesnt work

        return

    def __direct_dl(self, media_id, torrent=False):
        try:
            url = '%s/%s?apikey=%s' % (base_url, direct_dl_path, self.password)
            data = urllib.urlencode({'src': media_id})
            response = self.net.http_POST(url, form_data=data, headers=self.headers).content
            result = json.loads(response)
            if 'status' in result:
                if result.get('status') == 'success':
                    if torrent:
                        minimum_size = 75  # megabytes
                        for items in result.get("content"):
                            if items.get('size') >= ((1000**2) * minimum_size) and not items.get("stream_link") == "":
                                return items.get("stream_link", "")
                    else:
                        return result.get('location', "")
                else:
                    raise ResolverError('Link Not Found: Error Code: %s' % result.get('status'))
            else:
                raise ResolverError('Unexpected Response Received')
        except:
            pass

        return ""

    def __list_folders(self):
        try:
            url = '%s/%s?apikey=%s' % (base_url, list_folders_path, self.password)
            response = self.net.http_GET(url, headers=self.headers).content
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
                url = '%s/%s?apikey=%s' % (base_url, create_folder_path, self.password)
                data = urllib.urlencode({'name': folder_name})
                response = self.net.http_POST(url, form_data=data, headers=self.headers).content
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
                url = '%s/%s?apikey=%s' % (base_url, delete_folder_path, self.password)
                data = urllib.urlencode({'id': folder_id})
                response = self.net.http_POST(url, form_data=data, headers=self.headers).content
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
            url = '%s/%s?apikey=%s' % (base_url, clear_finished_path, self.password)
            result = self.net.http_POST(url, form_data={}, headers=self.headers).content
            result = json.loads(result)
            if 'status' in result:
                if result.get('status') == 'success':
                    logger.log_debug('Finished transfers successfully cleared from the Premiumize.me cloud')
                    return True
        except:
            pass

        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_torrents" type="bool" label="%s" default="true"/>' % (cls.__name__, i18n('torrents')))
        xml.append('<setting id="%s_login" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('login')))
        xml.append('<setting id="%s_password" enable="eq(-1,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('api_key')))
        return xml

    @classmethod
    def isUniversal(cls):
        return True
