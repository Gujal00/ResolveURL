"""
    Plugin for ResolveURL
    Copyright (C) 2019 twilight0

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


import re  # , traceback, sys
from six.moves import urllib_parse
import json
from os.path import join, exists
from os import remove
import time
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

USER_AGENT = 'ResolveURL for Kodi/{0}'.format(common.addon_version)

base_url = 'https://linksnappy.com'
api = '/'.join([base_url, 'api'])
authenticate = '/'.join([api, 'AUTHENTICATE'])
# filehosts = '/'.join([api, 'FILEHOSTS'])  # Does not update itself as often as the one below
filehosts = '/'.join([api, 'FILEHOSTSREALTIME'])
regexarr = '/'.join([api, 'REGEXARR'])
hostcachecheck = '/'.join([api, 'HOSTCACHECHECK?link={0}'])
cachedlstatus = '/'.join([api, 'CACHEDLSTATUS?id={0}'])

# user_details = '/'.join([api, 'USERDETAILS'])  # Does not work well with cookies
# torrents_genzip = '/'.join([torrents, 'GENZIP'])  # provides a zip-file of a torrent, not used in resolveurl
# toggle_download_log = '/'.join([api, 'TOGGLEDOWNLOADLOG?state={0}'])  # can toggle download logs, state=on or state=off, not currently used in the plugin

# regex = '/'.join([api, 'REGEX'])  # single regex pattern, not particularly useful

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
torrents_create = '/'.join([torrents, 'CREATEFOLDER?name={0}&dir={1}'])  # add param dir for creating a subfolder
torrents_rename = '/'.join([torrents, 'RENAMEFOLDER?name={0}&fid={1}'])
torrents_deletefile = '/'.join([torrents, 'DELETEFILE?fid={0}'])
torrents_delete = '/'.join([torrents, 'DELETETORRENT?tid={0}&delFiles={1}'])
torrents_move = '/'.join([torrents, 'MOVETORRENTFILE?fid={0}&dir={1}'])
torrents_links = '/'.join([torrents, 'DOWNLOADLINKS?fid={0}'])
torrents_hashcheck = '/'.join([torrents, 'HASHCHECK?{0}'])

folder_name = 'resolveurl'


# noinspection PyBroadException
class LinksnappyResolver(ResolveUrl):

    name = "Linksnappy"
    domains = ["*"]
    media_url = None
    cookie_file = join(common.profile_path, '{0}.cookies'.format(name))

    def __init__(self):

        self.hosts = None
        self.patterns = None
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

        if media_id.lower().startswith('magnet:') or '.torrent' in media_id.lower():

            if cached:

                logger.log_debug('Linksnappy.com: "{0}" is readily available to stream'.format(media_id))

                torrent_id = self.__create_transfer(media_id)

            else:

                if self.get_setting('cached_only') == 'true' or cached_only:

                    raise ResolverError('Linksnappy.com: Cached torrents are only allowed to be initiated')

                else:

                    logger.log_debug('Linksnappy.com: initiating transfer to files for "{0}"'.format(media_id))

                    torrent_id = self.__initiate_transfer(media_id)

            # self.__delete_folder()

            link = self.__direct_dl(media_id=torrent_id, torrent=True)

            # Disabled by default:
            # try:
            #
            #     if link is not None:
            #
            #         self.__clear_finished(torrent_id)
            #
            # except Exception:
            #
            #     pass

        else:

            in_list = any(item in media_id for item in self.get_hosts()[1]) or any(item in host for item in self.get_hosts()[1])

            if cached and in_list:

                logger.log_debug('Linksnappy.com: "{0}" is readily available to stream'.format(media_id))

            elif (self.get_setting('cached_files_only') == 'true' or cached_only) and not cached and in_list:

                raise ResolverError('Linksnappy.com: Cached files from hosts are only allowed to be initiated')

            link = self.__direct_dl(media_id)

        if link is not None:

            logger.log_debug('Linksnappy.com: Successfully resolved url to "{0}"'.format(link))

            return link + helpers.append_headers(self.headers)

        raise ResolverError('Link Not Found')

    def get_url(self, host, media_id):

        return media_id

    def get_host_and_id(self, url):

        return 'linksnappy.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):

        _hosts = []
        disabled = []
        cached = []

        try:

            if self.get_setting('torrents') == 'true':
                _hosts.extend(['torrent', 'magnet'])

            response = self.net.http_GET(filehosts, headers=self.headers).content

            res = json.loads(response)

            if res.get('status') != 'OK':

                raise ResolverError('Server did not return hosts list')

            result = iter(list(res.get('return').items()))

            for h, d in result:

                if d['Status'] == '0':
                    disabled.append(h)
                    continue
                elif h == 'mp3':
                    continue
                elif d['iscacheable'] == 1:
                    cached.append(h)

                _hosts.append(h)

                if 'alias' in d:
                    for a in d['alias']:
                        _hosts.append(a)

            logger.log_debug('Linksnappy.com available hosts: {0}'.format(_hosts))
            logger.log_debug('Linksnappy.com hosts supporting cache: {0}'.format(cached))

            if disabled:

                logger.log_debug('Linksnappy.com currently disabled hosts: {0}'.format(disabled))

            return _hosts, cached

        except Exception as e:

            logger.log_error('Error getting Linksnappy hosts: {0}'.format(e))

        return [], []

    @common.cache.cache_method(cache_limit=8)
    def get_regexes(self):

        try:

            pattern = self.net.http_GET(regexarr, headers=self.headers).content

            json_object = json.loads(pattern)

            if json_object.get('error') is not False:

                raise Exception('Unexpected response received when attempting reading regex patterns')

            else:

                logger.log_debug('Linksnappy.com hosts patterns: {0}'.format(repr(json_object.get('return'))))

            regex_list = [re.compile(i[1:-1]) for i in list(json_object.get('return').values()) if i]

            return regex_list

        except Exception as e:

            logger.log_error('Error getting Linksnappy regex pattern: {0}'.format(e))

        return []

    def valid_url(self, url, host):

        if url:

            if (url.lower().startswith('magnet:') or '.torrent' in url.lower()) and self.get_setting('torrents') == 'true':

                return True

            if self.patterns is None:

                self.patterns = self.get_regexes()

            for p in self.patterns:

                if p.search(url):

                    return True

        elif host:

            if self.hosts is None:

                self.hosts = self.get_hosts()[0]

            if host.startswith('www.'):

                host = host.replace('www.', '')

            if any(item in host for item in self.hosts):

                return True

        return False

    def __check_cache(self, media_id):

        _url = media_id

        if _url.startswith('magnet:'):

            media_id = re.search(r'btih:(\w+)', media_id).group(1)

        else:

            media_id = urllib_parse.quote_plus(media_id)

        try:

            if _url.startswith('magnet:'):
                check_url = torrents_hashcheck.format(''.join(['hash=', media_id]))
            elif '.torrent' in _url:
                check_url = torrents_hashcheck.format(''.join(['url=', media_id]))
            else:
                check_url = hostcachecheck.format(media_id)

            res = self.net.http_GET(check_url, headers=self.headers).content
            result = json.loads(res)

            if result.get('status') == 'OK':

                return result.get('return') == 'CACHED'

        except Exception:

            logger.log_debug('Linksnappy.com failure on retrieving cache status')

        return False

    def __check_dl_status(self, hash_id):

        response = self.net.http_GET(cachedlstatus.format(hash_id), headers=self.headers).content

        result = json.loads(response)

        if result.get('status') != 'OK':

            raise ResolverError('Error occured when checking host transfer dl status')

        return result.get('return')

    def __create_transfer(self, media_id):

        try:

            if media_id.startswith('magnet:'):
                response = self.net.http_GET(torrents_addmagnet.format(urllib_parse.quote_plus(media_id)), headers=self.headers).content
            else:
                response = self.net.http_GET(torrents_addurl.format(urllib_parse.quote_plus(media_id)), headers=self.headers).content

            result = json.loads(response)

            if media_id.startswith('magnet:'):

                if result.get('status') == 'OK' and result.get('error') is False:

                    torrent = result.get('return')[0]

                    error = torrent.get('error')

                    torrent_id = torrent.get('torrentid')

                    if error:

                        logger.log_debug('Linksnappy error at line 332: ' + error)

                else:

                    raise ResolverError('Unexpected response received when attempting to add a torrent')

            else:

                if list(result.keys())[0].endswith('.torrent'):

                    torrent_id = list(result.values())[0].get('torrentid')

                    error = list(result.values())[0].get('error')

                    if error:

                        logger.log_debug('Linksnappy error at line 348:' + error)

                else:

                    raise ResolverError('Unexpected response received when attempting to add a torrent')

            if torrent_id:

                logger.log_debug('Linksnappy.com: Added the following url for transfer {0}'.format(media_id))

            folder_id = self.__create_folder()

            result = self.__start_transfer(torrent_id, folder_id)

            if result.get('error') is False:

                logger.log_debug('Linksnappy transfer with torrent id: "{0}" successfully started'.format(torrent_id))

            else:

                logger.log_debug('Linksnappy transfer with torrent id "{0}" has the following error: {1}'.format(torrent_id, result.get('error')))

                if result.get('error') == 'Magnet URI processing in progress. Please wait.':

                    count = 1
                    while self.__start_transfer(torrent_id, folder_id).get('error') is not False:

                        logger.log_debug('Waiting for Linksnappy transfer due to the following status: "{0}"'.format(result.get('error')))

                        common.kodi.sleep(3000)
                        count += 1
                        if count == 8:
                            raise ResolverError('Linksnappy torrens: Waited too long for transfer to start')

            return str(torrent_id)

        except Exception as e:

            logger.log_debug('Linksnappy error at __create_transfer: {0}'.format(e))

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
            line2 = ''.join([i18n('download_rate'), ' ', str(transfer_info.get('downloadRate'))])
            line3 = ''.join(
                [
                    i18n('peer_number'), ' ', str(transfer_info.get('getPeers'))
                ]
            )

            with common.kodi.ProgressDialog('ResolveURL Linksnappy transfer', line1, line2, line3) as pd:

                while transfer_info.get('status') != 'FINISHED':

                    common.kodi.sleep(2000)
                    transfer_info = self.__list_transfer(torrent_id)

                    try:

                        line1 = transfer_info.get('name')
                        line2 = ''.join([i18n('download_rate'), ' ', str(transfer_info.get('downloadRate'))])
                        line3 = ''.join(
                            [
                                i18n('peer_number'), ' ', str(transfer_info.get('getPeers')), ', ETA: ',
                                str(transfer_info.get('eta')), ' ', i18n('seconds')
                            ]
                        )

                        logger.log_debug(line2)

                        pd.update(int(transfer_info.get('percentDone')), line1=line1, line2=line2, line3=line3)

                    except ValueError:

                        pass

                    if pd.is_canceled():

                        self.__delete_transfer(torrent_id)
                        # self.__delete_folder()
                        raise ResolverError('Transfer ID "{0}" canceled by user'.format(torrent_id))

                else:

                    logger.log_debug('Linksnappy.com: Transfer with id "{0}" completed!'.format(torrent_id))

                    common.kodi.sleep(1000 * interval)  # allow api time to generate the stream_link

                    return torrent_id

    def __direct_dl(self, media_id, torrent=False):

        try:

            if torrent:

                response = self.net.http_GET(torrents_files.format(media_id), headers=self.headers).content

            else:

                response = self.net.http_GET(linkgen.format(urllib_parse.quote_plus('{"link":"%s"}' % media_id)), headers=self.headers).content

            result = json.loads(response)

            if torrent:

                if result.get('status') == 'OK':

                    _videos = []

                    def _search_tree(d):

                        for v in list(d.items()):
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

                stream = result.get('links')[0]

                if stream['status'] != 'OK':

                    raise ResolverError('Link Not Found: {0}'.format(stream.get('error')))

                elif stream['type'] != 'video':

                    raise ResolverError(
                        'Generated link "{0}" does not contain a playable file'.format(stream.get('generated'))
                    )

                elif any(item in media_id for item in self.get_hosts()[1]):

                    transfer_info = self.__check_dl_status(stream.get('hash'))

                    if transfer_info.get('percent') != 100:

                        line1 = stream.get('filename')
                        line2 = stream.get('filehost')

                        with common.kodi.ProgressDialog('ResolveURL Linksnappy transfer', line1, line2) as pd:

                            while self.__check_dl_status(stream.get('hash')).get('percent') != 100:

                                common.kodi.sleep(2000)

                                transfer_info = self.__check_dl_status(stream.get('hash'))

                                try:

                                    logger.log_debug(
                                        'Transfer with id "{0}" is still in progress, caching... active connections {1}, download speed {2}'.format(
                                            stream.get('hash'), transfer_info.get('connections'), transfer_info.get('downloadSpeed')
                                        )
                                    )

                                except ValueError:

                                    pass

                                try:

                                    line1 = stream.get('filename')
                                    line2 = stream.get('filehost')

                                    try:

                                        line3 = ''.join(
                                            [i18n('download_rate'), ' ', transfer_info.get('downloadSpeed')]
                                        )

                                        pd.update(int(transfer_info.get('percent')), line1=line1, line2=line2, line3=line3)

                                    except ValueError:

                                        pd.update(int(transfer_info.get('percent')), line1=line1, line2=line2)

                                except ValueError:

                                    pass

                                if pd.is_canceled():

                                    raise ResolverError('Transfer ID "{0}" canceled by user'.format(stream.get('hash')))

                            else:

                                logger.log_debug('Transfer with id "{0}" completed'.format(stream.get('hash')))
                                pd.update(percent=100)
                                return stream.get('generated')

                    else:

                        stream.get('generated')

                return stream.get('generated')

        except Exception as e:

            # _, __, tb = sys.exc_info()
            #
            # print traceback.print_tb(tb)

            logger.log_debug('Linksnappy, error at __direct_dl function: {0}'.format(e))

        return None

    def __list_folders(self):

        try:

            response = self.net.http_GET(torrents_folderlist, headers=self.headers).content
            result = json.loads(response)

            if result.get('status') == 'OK' and not result.get('error'):

                for items in result.get("return")[::-1]:

                    if items.get('type') == 'root' and (items.get('text') == folder_name or items.get('text') == 'Downloads'):

                        return items.get('id', ''), items.get('text', '')

        except Exception:

            pass

        return ''

    def __create_folder(self):

        folder_id, f_name = self.__list_folders()

        if f_name == folder_name:

            return folder_id

        elif f_name == 'Downloads':

            try:

                response = self.net.http_GET(torrents_create.format(folder_name, folder_id), headers=self.headers).content
                result = json.loads(response)

                if result.get('status') == 'OK':

                    logger.log_debug('Created new folder named "{0}" at Linksnappy files'.format(folder_name))

                    folder_id = result.get('return').get('id')

                    return folder_id

            except Exception:

                pass

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

                logger.log_debug('Successfully cleared torrent with id {0} from Linksnappy torrents'.format(torrent_id))

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

        if exists(self.cookie_file):

            remove(self.cookie_file)

        if not self.get_setting('username') or not self.get_setting('password'):

            username = common.kodi.get_keyboard(i18n('username'))
            password = common.kodi.get_keyboard(i18n('password'), hide_input=True)

            if username and password:

                self.set_setting('username', username)
                self.set_setting('password', password)

                login_query = '?{0}'.format(urllib_parse.urlencode({'username': username, 'password': password}))

            else:

                raise ResolverError('Linksnappy Error: {0}'.format('Did not provide both username and password'))

        else:

            login_query = '?{0}'.format(
                urllib_parse.urlencode({'username': self.get_setting('username'), 'password': self.get_setting('password')})
            )

        response = self.net.http_GET(url=''.join([authenticate, login_query]), headers=self.headers).content

        res = json.loads(response)

        if 'OK' in res.get('status'):

            self.net.save_cookies(self.cookie_file)
            self.__update_timestamp()

            common.kodi.notify(msg=i18n('ls_authorized'))

            return True

        elif 'ERROR' in res.get('status'):

            self.set_setting('username', '')
            self.set_setting('password', '')
            remove(self.cookie_file)

            raise ResolverError('Linksnappy Error: {0}'.format(res.get('error')))

    def reset_authorization(self):

        remove(self.cookie_file)
        self.set_setting('username', '')
        self.set_setting('password', '')
        self.set_setting('expiration_timestamp', '')

    @classmethod
    def _is_enabled(cls):

        return cls.get_setting('enabled') == 'true' and exists(cls.cookie_file)

    @classmethod
    def get_settings_xml(cls):

        xml = super(cls, cls).get_settings_xml()

        xml.append(
            '<setting id="{0}_username" enable="eq(-1,true)" type="text" label="{1}" visible="false" default=""/>'.format(
                cls.__name__, i18n('username')
            )
        )

        xml.append(
            '<setting id="{0}_password" enable="eq(-2,true)" type="text" label="{1}" visible="false" default=""/>'.format(
                cls.__name__, i18n('password')
            )
        )

        xml.append(
            '<setting id="{0}_auth" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_ls)" option="close"/>'.format(
                cls.__name__, i18n('auth_my_account')
            )
        )

        xml.append(
            '<setting id="{0}_reset" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_ls)"/>'.format(
                cls.__name__, i18n('reset_my_auth')
            )
        )

        xml.append(
            '<setting id="{0}_cached_files_only" type="bool" label="{1}" default="false" />'.format(
                cls.__name__, i18n('cached_files_only')
            )
        )

        xml.append(
            '<setting id="{0}_torrents" type="bool" label="{1}" default="true"/>'.format(
                cls.__name__, i18n('torrents')
            )
        )

        xml.append(
            '<setting id="{0}_cached_only" enable="eq(-1,true)" type="bool" label="{1}" default="true" />'.format(
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
