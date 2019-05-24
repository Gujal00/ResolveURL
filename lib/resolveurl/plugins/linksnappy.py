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
from urllib import urlencode, quote
import json
from os.path import join, exists
from os import remove
import time, sys, traceback

from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

USER_AGENT = 'ResolveURL for Kodi/{0}'.format(common.addon_version)

base_url = 'https://linksnappy.com'
api = '/'.join([base_url, 'api'])
authenticate = '/'.join([api, 'AUTHENTICATE'])
filehosts = '/'.join([api, 'FILEHOSTS'])
regexarr = '/'.join([api, 'REGEXARR'])

# regex = '/'.join([api, 'REGEX'])  # single regex pattern, not particularly useful
user_details = '/'.join([api, 'USERDETAILS'])
# torrents_genzip = '/'.join([torrents, 'GENZIP'])  # provides a zip-file of a torrent, not used in resolveurl

toggle_download_log = '/'.join([api, 'TOGGLEDOWNLOADLOG?state={0}'])  # can toggle download logs, state=on or state=off
deletelink = '/'.join([api, 'DELETELINK'])
linkgen = '/'.join([api, 'linkgen?genLinks={0}'])

torrents = '/'.join([api, 'torrents'])
torrents_addmagnet = '/'.join([torrents, 'ADDMAGNET?magnetlinks={0}'])
torrents_addurl = '/'.join([torrents, 'ADDURL?url={0}'])
torrents_start = '/'.join([torrents, 'START?tid={0}&fid={1}'])
torrents_list = '/'.join([torrents, 'LIST'])
torrents_files = '/'.join([torrents, 'FILES?id={0}'])
torrents_folderlist = '/'.join([torrents, 'FOLDERLIST'])
torrents_status = '/'.join([torrents, 'STATUS?tid={0}'])
torrents_create = '/'.join([torrents, 'CREATEFOLDER?name={0}'])  # add param dir for creating a subfolder
torrents_rename = '/'.join([torrents, 'RENAMEFOLDER?name={0}&fid={1}'])
torrents_deletefile = '/'.join([torrents, 'DELETEFILE?fid={0}'])
torrents_delete = '/'.join([torrents, 'DELETETORRENT?tid={0}&delFiles={1}'])
torrents_move = '/'.join([torrents, 'MOVETORRENTFILE?fid={0}&dir={1}'])
torrents_links = '/'.join([torrents, 'DOWNLOADLINKS?fid={0}'])
torrents_hash_check = '/'.join([torrents, 'HASHCHECK?hash={0}'])
torrents_url_check = '/'.join([torrents, 'HASHCHECK?url={0}'])

folder_name = 'resolveurl'


# noinspection PyBroadException
class LinksnappyResolver(ResolveUrl):

    name = "Linksnappy"
    domains = ["*"]
    media_url = None
    cookie_file = join(common.profile_path, '{0}.cookies'.format(name))

    def __init__(self):

        self.hosts = []
        self.patterns = []
        self.net = common.Net()
        self.headers = {'User-Agent': USER_AGENT}

        if exists(self.cookie_file):

            try:
                expired = float(self.get_setting('expiration_timestamp')) < time.time()
            except ValueError:
                expired = True

            if expired:

                if self.authorize_resolver():

                    self.net.set_cookies(self.cookie_file)

            else:

                self.__update_timestamp()
                self.net.set_cookies(self.cookie_file)

    def get_media_url(self, host, media_id, cached_only=False):

        cached = self.__check_cache(media_id)
        media_id_lc = media_id.lower()

        if media_id_lc.startswith('magnet:') or '.torrent' in media_id_lc:

            if cached:

                logger.log_debug('Linksnappy.com: {0} is readily available to stream'.format(media_id))

                torrent_id = self.__create_transfer(media_id)

            else:

                if self.get_setting('cached_only') == 'true' or cached_only:

                    raise ResolverError('Linksnappy.com: Cached torrents only allowed to be initiated')

                else:

                    logger.log_debug('Linksnappy.com: initiating transfer to files for {0}'.format(media_id))

                    torrent_id = self.__initiate_transfer(media_id)

            # self.__delete_folder()

            link = self.__direct_dl(media_id=torrent_id, torrent=True)

            try:

                if link is not None:

                    self.__clear_finished(torrent_id)

            except Exception:

                pass

        else:

            link = self.__direct_dl(media_id)

        if link is not None:

            logger.log_debug('Linksnappy.com: Successfully resolved url to {0}'.format(link))

            return link + helpers.append_headers(self.headers)

        raise ResolverError('Link Not Found')

    def get_url(self, host, media_id):

        return media_id

    def get_host_and_id(self, url):

        return 'linksnappy.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):

        try:

            _hosts = []
            disabled = []

            response = self.net.http_GET(user_details, headers=self.headers).content
            details = json.loads(response).get('return')

            torrent_access = details.get('torrentAccess')
            account_type = details.get('accountType')

            if self.get_setting('torrents') == 'true' and torrent_access:
                _hosts.extend([u'torrent', u'magnet'])

            if account_type == 'elite':

                response = self.net.http_GET(filehosts, headers=self.headers).content
                res = json.loads(response)

                if res.get('status') != 'OK':

                    raise ResolverError('Server did not return hosts list')

                result = res.get('return').iteritems()

                for h, d in result:

                    if d['Status'] == '0':
                        disabled.append(h)
                        continue

                    _hosts.append(h)
                    if 'alias' in d:
                        for a in d['alias']:
                            _hosts.append(a)

                logger.log_debug('Linksnappy.com available hosts: {0}'.format(_hosts))

                if disabled:

                    logger.log_debug('Linksnappy.com currently disabled hosts: {0}'.format(disabled))

                pattern = self.net.http_GET(regexarr, headers=self.headers).content

                json_object = json.loads(pattern)

                if json_object.get('error') is not False:

                    raise Exception, 'Unexpected response received when attempting reading regex patterns'

                else:

                    logger.log_debug('Linksnappy.com hosts pattern: {0}'.format(repr(json_object.get('return').values())))

                regex_list = [re.compile(i[1:-1]) for i in json_object.get('return').values() if i]

                return _hosts, regex_list

            elif account_type == 'torrent':

                return _hosts, []

        except Exception as e:

            logger.log_error('Error getting Linksnappy hosts: {0}'.format(e))

        return [], []

    def valid_url(self, url, host):

        if url and self.get_setting('torrents') == 'true':

            url_lc = url.lower()

            if url_lc.endswith('.torrent') or url_lc.startswith('magnet:'):

                return True

        if not self.patterns or not self.hosts:

            self.hosts, self.patterns = self.get_all_hosters()

        if url:

            for pattern in self.patterns:

                if pattern.search(url):

                    return True

        elif host:

            if host.startswith('www.'):

                host = host.replace('www.', '')

            if any(host in item for item in self.hosts):

                return True

        return False

    def __check_cache(self, media_id):

        _url = media_id

        if _url.startswith('magnet:'):

            media_id = re.search(r'btih:(\w+)', media_id).group(1)

        try:

            if _url.startswith('magnet:'):
                check_url = torrents_hash_check.format(media_id)
            elif '.torrent' in media_id:
                check_url = torrents_url_check.format(quote(media_id))
            else:
                return False

            res = self.net.http_GET(check_url, headers=self.headers).content
            result = json.loads(res)

            if result.get('status') == 'OK':

                return result.get('return') == 'CACHED'

        except Exception:

            logger.log_debug('Linksnappy.com failure on retrieving cache status')

        return False

    def __create_transfer(self, media_id):

        folder_id = self.__create_folder()

        if folder_id != '':

            try:

                if media_id.startswith('magnet:'):
                    response = self.net.http_GET(torrents_addmagnet.format(quote(media_id)), headers=self.headers).content
                else:
                    response = self.net.http_GET(torrents_addurl.format(quote(media_id)), headers=self.headers).content

                result = json.loads(response)

                if media_id.startswith('magnet:'):

                    if result.get('status') == 'OK' and result.get('error') is False:

                        error = result.get('return')[0].get('error')

                        torrent_id = result.get('return')[0].get('torrentid')

                        if error is not False:

                            logger.log_debug(error)

                    else:

                        raise ResolverError('Unexpected response received when attempting to add a torrent')

                else:

                    if result.keys()[0].endswith('.torrent'):

                        torrent_id = result.values()[0].get('torrentid')

                        error = result.values()[0].get('error')

                        if error is not False:

                            logger.log_debug(error)

                    else:

                        raise ResolverError('Unexpected response received when attempting to add a torrent')

                if torrent_id:

                    logger.log_debug('Linksnappy.com: Added the following url for transfer {0}'.format(media_id))

                result = self.__start_transfer(torrent_id, folder_id)

                logger.log_debug(result)

                if result.get('error') is False:

                    logger.log_debug('Linksnappy transfer with torrent id: {0} successfully started'.format(torrent_id))

                else:

                    logger.log_debug('Linksnappy transfer with torrent id {0} has the following error: {1}'.format(torrent_id, result.get('error')))

                    if result.get('error') == 'Magnet URI processing in progress. Please wait.':

                        while self.__start_transfer(torrent_id, folder_id).get('error') is not False:

                            logger.log_debug('Waiting for Linksnappy transfer due to the following status: {0}'.format(torrent_id, result.get('error')))

                            common.kodi.sleep(3000)

                return str(torrent_id)

            except Exception:

                pass

        return ''

    def __start_transfer(self, torrent_id, folder_id):

        response = self.net.http_GET(torrents_start.format(torrent_id, folder_id), headers=self.headers).content

        result = json.loads(response)

        return result

    def __list_transfer(self, torrent_id):

        if torrent_id != '':

            try:

                response = self.net.http_GET(torrents_status.format(torrent_id), headers=self.headers).content

                result = json.loads(response).get('return')

                return result

            except Exception:

                pass

        return {}

    def __delete_transfer(self, transfer_id):

        if transfer_id != '':

            try:

                response = self.net.http_GET(torrents_delete.format(transfer_id, '1'), headers=self.headers).content
                result = json.loads(response)

                if result.get('status') == 'OK' and result.get('error') is False:

                    logger.log_debug('Transfer ID "{0}" deleted from the Linksnappy files & torrents'.format(transfer_id))

                    return True

            except Exception:

                pass

        return False

    def __initiate_transfer(self, media_id, interval=5):

        torrent_id = self.__create_transfer(media_id)

        transfer_info = self.__list_transfer(torrent_id)

        if transfer_info:

            line1 = transfer_info.get('name')
            line2 = 'Saving torrent to the Linksnappy Files'
            line3 = ''.join([i18n('download_rate'), ' ', str(transfer_info.get('downloadRate'))])

            with common.kodi.ProgressDialog('Resolve URL Linksnappy Transfer', line1, line2, line3) as pd:

                while transfer_info.get('status') != 'FINISHED':

                    common.kodi.sleep(1000 * interval)
                    transfer_info = self.__list_transfer(torrent_id)
                    line1 = transfer_info.get('name')

                    line3 = ''.join([i18n('download_rate'), ' ', str(transfer_info.get('downloadRate'))])

                    logger.log_debug(line3)

                    try:
                        pd.update(int(transfer_info.get('percentDone')), line1=line1, line3=line3)
                    except ValueError:
                        pass

                    if pd.is_canceled():

                        self.__delete_transfer(torrent_id)
                        # self.__delete_folder()
                        raise ResolverError('Transfer ID {0} canceled by user'.format(torrent_id))

                else:

                    logger.log_debug('Linksnappy.com: Transfer completed')

                    common.kodi.sleep(1000 * interval)  # allow api time to generate the stream_link

                    return torrent_id

    def __direct_dl(self, media_id, torrent=False):

        try:

            if torrent:

                response = self.net.http_GET(torrents_files.format(media_id)).content

            else:

                response = self.net.http_GET(linkgen.format(quote('{"link":"%s"}' % media_id))).content

            result = json.loads(response)

            logger.log_debug(result)

            if torrent:

                if result.get('status') == 'OK':

                    _videos = []

                    def _search_tree(d):

                        for k, v in d.items():
                            if isinstance(v, dict) and v.get('isVideo') != 'y':
                                _search_tree(v)
                            else:
                                if isinstance(v, dict):
                                    _videos.append(v)

                    _search_tree(result)

                    try:

                        link = max(_videos, key=lambda x: int(x.get('size'))).get('downloadLink', None)

                        stream = self.net.http_GET(link, headers=self.headers).get_url()

                        return stream

                    except Exception:

                        raise ResolverError('Failed to locate largest video file')

                else:

                    raise ResolverError('Unexpected Response Received')

            else:

                try:

                    stream = result.get('links')[0]

                    if stream['status'] != 'OK':

                        raise ResolverError('Link Not Found: {0}'.format(result.get('error')))

                    return stream.get('generated')

                except Exception:

                    raise ResolverError('Unexpected Response Received')

        except Exception:

            _, __, tb = sys.exc_info()

            print traceback.print_tb(tb)

        return None

    def __list_folders(self):

        try:

            response = self.net.http_GET(torrents_folderlist, headers=self.headers).content
            result = json.loads(response)

            if result.get('status') == 'OK' and not result.get('error'):

                for items in result.get("return")[::-1]:

                    if items.get('type') == 'root' and items.get('text') == folder_name or items.get('text') == 'Downloads':

                        return items.get('id', '')

        except Exception:

            pass

        return ''

    def __create_folder(self):

        folder_id = self.__list_folders()

        if folder_id == '':

            try:

                response = self.net.http_GET(torrents_create.format(folder_name), headers=self.headers).content
                result = json.loads(response)

                if result.get('status') == 'OK':

                    logger.log_debug('Created new folder named "{0}" into Linksnappy files'.format(folder_name))

                    folder_id = result.get('return').get('id')

                    return folder_id

            except Exception:

                pass

        else:

            return folder_id

        return ''

    def __delete_folder(self):

        folder_id = self.__list_folders()

        if folder_id != '':

            try:

                response = self.net.http_GET(torrents_deletefile.format(folder_id), headers=self.headers).content
                result = json.loads(response)

                if 'status' in result:

                    if result.get('status') == 'OK':

                        logger.log_debug('Folder named "{0}" deleted from the Linksnappy files'.format(folder_name))

                        return True

            except Exception:

                pass

        return False

    def __clear_finished(self, torrent_id):

        try:

            result = self.net.http_GET(torrents_delete.format(torrent_id, '0'), headers=self.headers).content
            result = json.loads(result)

            if result.get('status') == 'OK':

                logger.log_debug('Finished transfers successfully cleared from the Linksnappy torrents')

                return True

        except Exception:

            pass

        return False

    def __update_timestamp(self):

        current_ts = time.time()
        expiration_timestamp = current_ts + 2592000.0  # cookies are valid for one month if no request is made

        self.set_setting('expiration_timestamp', expiration_timestamp)

    # SiteAuth methods
    def login(self):

        if not exists(self.cookie_file):

            self.authorize_resolver()

    def authorize_resolver(self):

        self.login_query = '?{0}'.format(
            urlencode({'username': self.get_setting('username'), 'password': self.get_setting('password')})
        )

        response = self.net.http_GET(url=''.join([authenticate, self.login_query]), headers=self.headers).content

        res = json.loads(response)

        if 'OK' in res.get('status'):

            self.net.save_cookies(self.cookie_file)
            self.__update_timestamp()

            common.kodi.notify(msg=i18n('ls_authorized'))

            return True

        elif 'ERROR' in res.get('status'):

            raise ResolverError('Linksnappy Error: {0}'.format(res.get('error')))

    def reset_authorization(self):

        remove(self.cookie_file)
        self.set_setting('expiration_timestamp', '')

    @classmethod
    def _is_enabled(cls):

        return cls.get_setting('enabled') == 'true' and exists(cls.cookie_file)

    @classmethod
    def get_settings_xml(cls):

        xml = super(cls, cls).get_settings_xml()
        xml.append(
            '<setting id="{0}_username" enable="eq(-1,true)" type="text" label="{1}" default=""/>'.format(
                cls.__name__, i18n('username')
            )
        )

        xml.append(
            '<setting id="{0}_password" enable="eq(-2,true)" type="text" label="{1}" option="hidden" default=""/>'.format(
                cls.__name__, i18n('password')
            )
        )

        xml.append(
            '<setting id="{0}_auth" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_ls)"/>'.format(
                cls.__name__, i18n('auth_my_account')
            )
        )

        xml.append(
            '<setting id="{0}_reset" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_ls)"/>'.format(
                cls.__name__, i18n('reset_my_auth')
            )
        )

        xml.append(
            '<setting id="{0}_torrents" type="bool" label="{1}" default="true"/>'.format(
                cls.__name__, i18n('torrents')
            )
        )

        xml.append(
            '<setting id="{0}_cached_only" enable="eq(-1,true)" type="bool" label="{1}" default="false" />'.format(
                cls.__name__, i18n('cached_only')
            )
        )

        xml.append(
            '<setting id="{0}_expiration_timestamp" label="Linksnappy expiration timestamp" visible="false" type="text" default=""/>'.format(
                cls.__name__
            )
        )

        return xml

    @classmethod
    def isUniversal(cls):

        return True
