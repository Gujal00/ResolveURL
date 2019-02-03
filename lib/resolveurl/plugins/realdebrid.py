"""
    ResolveURL Addon for Kodi
    Copyright (C) 2016 t0mm0, tknorris, jsergio

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
import urllib2
import json
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

CLIENT_ID = 'X245A4XAIBGVM'
USER_AGENT = 'ResolveURL for Kodi/%s' % common.addon_version
INTERVALS = 5  # seconds
FORMATS = ['.aac', '.asf', '.avi', '.flv', '.m4a', '.m4v', '.mka', '.mkv', '.mp4', '.mpeg', '.nut', '.ogg']
STALLED = ['magnet_error', 'error', 'virus', 'dead']

rest_base_url = 'https://api.real-debrid.com/rest/1.0'
oauth_base_url = 'https://api.real-debrid.com/oauth/v2'
unrestrict_link_path = 'unrestrict/link'
device_endpoint_path = 'device/code'
token_endpoint_path = 'token'
authorize_endpoint_path = 'auth'
credentials_endpoint_path = 'device/credentials'
hosts_regexes_path = 'hosts/regex'
hosts_domains_path = 'hosts/domains'
add_magnet_path = 'torrents/addMagnet'
torrents_info_path = 'torrents/info'
select_files_path = 'torrents/selectFiles'
torrents_delete_path = 'torrents/delete'
check_cache_path = 'torrents/instantAvailability'


class RealDebridResolver(ResolveUrl):
    name = "Real-Debrid"
    domains = ["*"]

    def __init__(self):
        self.net = common.Net()
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id, retry=False, cached_only=False):
        try:
            self.headers.update({'Authorization': 'Bearer %s' % self.get_setting('token')})
            if media_id.lower().startswith('magnet:'):
                cached = self.__check_cache(media_id)
                if not cached and (self.get_setting('cached_only') == 'true' or cached_only):
                    raise ResolverError('Real-Debrid: Cached torrents only allowed to be initiated')
                torrent_id = self.__add_magnet(media_id)
                if not torrent_id == "":
                    torrent_info = self.__torrent_info(torrent_id)
                    heading = 'Resolve URL Real-Debrid Transfer'
                    line1 = torrent_info.get('filename')
                    status = torrent_info.get('status')
                    if status == 'magnet_conversion':
                        line2 = 'Converting MAGNET...'
                        line3 = '%s seeders' % torrent_info.get('seeders')
                        _TIMEOUT = 100  # seconds
                        with common.kodi.ProgressDialog(heading, line1, line2, line3) as cd:
                            while status == 'magnet_conversion' and _TIMEOUT > 0:
                                cd.update(_TIMEOUT, line1=line1, line3=line3)
                                if cd.is_canceled():
                                    self.__delete_torrent(torrent_id)
                                    raise ResolverError('Real-Debrid: Torrent ID %s canceled by user' % torrent_id)
                                elif any(x in status for x in STALLED):
                                    self.__delete_torrent(torrent_id)
                                    raise ResolverError('Real-Debrid: Torrent ID %s has stalled | REASON: %s' % (torrent_id, status))
                                _TIMEOUT -= INTERVALS
                                common.kodi.sleep(1000 * INTERVALS)
                                torrent_info = self.__torrent_info(torrent_id)
                                status = torrent_info.get('status')
                                line1 = torrent_info.get('filename')
                                line3 = '%s seeders' % torrent_info.get('seeders')
                        if status == 'magnet_conversion':
                            self.__delete_torrent(torrent_id)
                            raise ResolverError('Real-Debrid Error: MAGNET Conversion exceeded time limit')
                    if status == 'waiting_files_selection':
                        _videos = []
                        for _file in torrent_info.get('files'):
                            if any(_file.get('path').lower().endswith(x) for x in FORMATS):
                                _videos.append(_file)
                        try:
                            _video = max(_videos, key=lambda x: x.get('bytes'))
                            file_id = _video.get('id', 0)
                        except ValueError:
                            self.__delete_torrent(torrent_id)
                            raise ResolverError('Real-Debrid Error: Failed to locate largest video file')
                        file_selected = self.__select_file(torrent_id, file_id)
                        if not file_selected:
                            self.__delete_torrent(torrent_id)
                            raise ResolverError('Real-Debrid Error: Failed to select file')
                        else:
                            torrent_info = self.__torrent_info(torrent_id)
                            status = torrent_info.get('status')
                            if not status == 'downloaded':
                                file_size = round(float(_video.get('bytes')) / (1000 ** 3), 2)
                                if cached:
                                    line2 = 'Getting torrent from the Real-Debrid Cloud'
                                else:
                                    line2 = 'Saving torrent to the Real-Debrid Cloud'
                                line3 = status
                                with common.kodi.ProgressDialog(heading, line1, line2, line3) as pd:
                                    while not status == 'downloaded':
                                        common.kodi.sleep(1000 * INTERVALS)
                                        torrent_info = self.__torrent_info(torrent_id)
                                        line1 = torrent_info.get('filename')
                                        status = torrent_info.get('status')
                                        if status == 'downloading':
                                            line3 = 'Downloading %s GB @ %s mbps from %s peers, %s %% completed' % (file_size, round(float(torrent_info.get('speed')) / (1000**2), 2), torrent_info.get("seeders"), torrent_info.get('progress'))
                                        else:
                                            line3 = status
                                        logger.log_debug(line3)
                                        pd.update(int(float(torrent_info.get('progress'))), line1=line1, line3=line3)
                                        if pd.is_canceled():
                                            self.__delete_torrent(torrent_id)
                                            raise ResolverError('Real-Debrid: Torrent ID %s canceled by user' % torrent_id)
                                        elif any(x in status for x in STALLED):
                                            self.__delete_torrent(torrent_id)
                                            raise ResolverError('Real-Debrid: Torrent ID %s has stalled | REASON: %s' % (torrent_id, status))
                            # xbmc.sleep(1000 * INTERVALS)  # allow api time to generate the stream_link
                            media_id = torrent_info.get('links')[0]
                    self.__delete_torrent(torrent_id)
                if media_id.lower().startswith('magnet:'):
                    self.__delete_torrent(torrent_id)  # clean up just incase
                    raise ResolverError('Real-Debrid Error: Failed to transfer torrent to/from the cloud')

            url = '%s/%s' % (rest_base_url, unrestrict_link_path)
            data = {'link': media_id}
            result = self.net.http_POST(url, form_data=data, headers=self.headers).content
        except urllib2.HTTPError as e:
            if not retry and e.code == 401:
                if self.get_setting('refresh'):
                    self.refresh_token()
                    return self.get_media_url(host, media_id, retry=True)
                else:
                    self.reset_authorization()
                    raise ResolverError('Real Debrid Auth Failed & No Refresh Token')
            else:
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = js_result['error']
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise ResolverError('Real Debrid Error: %s (%s)' % (msg, e.code))
        except Exception as e:
            raise ResolverError('Unexpected Exception during RD Unrestrict: %s' % e)
        else:
            js_result = json.loads(result)
            links = []
            link = self.__get_link(js_result)
            if link is not None:
                links.append(link)
            if 'alternative' in js_result:
                for alt in js_result['alternative']:
                    link = self.__get_link(alt)
                    if link is not None:
                        links.append(link)

            return helpers.pick_source(links)

    def __check_cache(self, media_id):
        r = re.search('''magnet:.+?urn:([a-zA-Z0-9]+):([a-zA-Z0-9]+)''', media_id, re.I)
        if r:
            _hash, _format = r.group(2).lower(), r.group(1)
            try:
                url = '%s/%s/%s' % (rest_base_url, check_cache_path, _hash)
                result = self.net.http_GET(url, headers=self.headers).content
                js_result = json.loads(result)
                _hash_info = js_result.get(_hash, {})
                if isinstance(_hash_info, dict):
                    if len(_hash_info.get('rd')) > 0:
                        logger.log_debug('Real-Debrid: %s is readily available to stream' % _hash)
                        return _hash_info
            except Exception as e:
                common.logger.log_warning("Real-Debrid Error: CHECK CACHE | %s" % e)
                raise

        return {}

    def __torrent_info(self, torrent_id):
        try:
            url = '%s/%s/%s' % (rest_base_url, torrents_info_path, torrent_id)
            result = self.net.http_GET(url, headers=self.headers).content
            js_result = json.loads(result)
            return js_result
        except Exception as e:
            common.logger.log_warning("Real-Debrid Error: TORRENT INFO | %s" % e)
            raise

    def __add_magnet(self, media_id):
        try:
            url = '%s/%s' % (rest_base_url, add_magnet_path)
            data = {'magnet': media_id}
            result = self.net.http_POST(url, form_data=data, headers=self.headers).content
            js_result = json.loads(result)
            logger.log_debug('Real-Debrid: Sending MAGNET URL to the real-debrid cloud')
            return js_result.get('id', "")
        except Exception as e:
            common.logger.log_warning("Real-Debrid Error: ADD MAGNET | %s" % e)
            raise

    def __select_file(self, torrent_id, file_id):
        try:
            url = '%s/%s/%s' % (rest_base_url, select_files_path, torrent_id)
            data = {'files': file_id}
            self.net.http_POST(url, form_data=data, headers=self.headers)
            logger.log_debug('Real-Debrid: Selected file ID %s from Torrent ID %s to transfer' % (file_id, torrent_id))
            return True
        except Exception as e:
            common.logger.log_warning("Real-Debrid Error: SELECT FILE | %s" % e)
            return False

    def __delete_torrent(self, torrent_id):
        try:
            url = '%s/%s/%s' % (rest_base_url, torrents_delete_path, torrent_id)
            self.net.http_DELETE(url, headers=self.headers)
            logger.log_debug('Real-Debrid: Torrent ID %s was removed from your active torrents' % torrent_id)
            return True
        except Exception as e:
            common.logger.log_warning("Real-Debrid Error: DELETE TORRENT | %s" % e)
            raise

    def __get_link(self, link):
        if 'download' in link:
            if 'quality' in link:
                label = '[%s] %s' % (link['quality'], link['download'])
            else:
                label = link['download']
            return label, link['download']

    # SiteAuth methods
    def login(self):
        if not self.get_setting('token'):
            self.authorize_resolver()

    def refresh_token(self):
        client_id = self.get_setting('client_id')
        client_secret = self.get_setting('client_secret')
        refresh_token = self.get_setting('refresh')
        logger.log_debug('Refreshing Expired Real Debrid Token: |%s|%s|' % (client_id, refresh_token))
        if not self.__get_token(client_id, client_secret, refresh_token):
            # empty all auth settings to force a re-auth on next use
            self.reset_authorization()
            raise ResolverError('Unable to Refresh Real Debrid Token')

    def authorize_resolver(self):
        url = '%s/%s?client_id=%s&new_credentials=yes' % (oauth_base_url, device_endpoint_path, CLIENT_ID)
        js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        line1 = 'Go to URL: %s' % (js_result['verification_url'])
        line2 = 'When prompted enter: %s' % (js_result['user_code'])
        with common.kodi.CountdownDialog('Resolve URL Real Debrid Authorization', line1, line2, countdown=120, interval=js_result['interval']) as cd:
            result = cd.start(self.__check_auth, [js_result['device_code']])

        # cancelled
        if result is None:
            return
        return self.__get_token(result['client_id'], result['client_secret'], js_result['device_code'])
        
    def __get_token(self, client_id, client_secret, code):
        try:
            url = '%s/%s' % (oauth_base_url, token_endpoint_path)
            data = {'client_id': client_id, 'client_secret': client_secret, 'code': code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
            self.set_setting('client_id', client_id)
            self.set_setting('client_secret', client_secret)
            logger.log_debug('Authorizing Real Debrid: %s' % client_id)
            js_result = json.loads(self.net.http_POST(url, data, headers=self.headers).content)
            logger.log_debug('Authorizing Real Debrid Result: |%s|' % js_result)
            self.set_setting('token', js_result['access_token'])
            self.set_setting('refresh', js_result['refresh_token'])
            return True
        except Exception as e:
            logger.log_debug('Real Debrid Authorization Failed: %s' % e)
            return False

    def __check_auth(self, device_code):
        try:
            url = '%s/%s?client_id=%s&code=%s' % (oauth_base_url, credentials_endpoint_path, CLIENT_ID, device_code)
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except Exception as e:
            logger.log_debug('Exception during RD auth: %s' % e)
        else:
            return js_result

    def reset_authorization(self):
        self.set_setting('client_id', '')
        self.set_setting('client_secret', '')
        self.set_setting('token', '')
        self.set_setting('refresh', '')
    
    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.real-debrid.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        hosters = []
        try:
            url = '%s/%s' % (rest_base_url, hosts_regexes_path)
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
            regexes = [regex[1:-1].replace('\/', '/').rstrip('\\') for regex in js_result]
            logger.log_debug('RealDebrid hosters : %s' % regexes)
            hosters = [re.compile(regex, re.I) for regex in regexes]
        except Exception as e:
            logger.log_error('Error getting RD regexes: %s' % e)
        return hosters

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        try:
            url = '%s/%s' % (rest_base_url, hosts_domains_path)
            hosts = json.loads(self.net.http_GET(url, headers=self.headers).content)
            if self.get_setting('torrents') == 'true':
                hosts.extend([u'torrent', u'magnet'])
        except Exception as e:
            logger.log_error('Error getting RD hosts: %s' % e)
        logger.log_debug('RealDebrid hosts : %s' % hosts)
        return hosts

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    def valid_url(self, url, host):
        logger.log_debug('in valid_url %s : %s' % (url, host))
        if url:
            if url.lower().startswith('magnet:') and self.get_setting('torrents') == 'true':
                return True
            if self.hosters is None:
                self.hosters = self.get_all_hosters()
                
            for host in self.hosters:
                # logger.log_debug('RealDebrid checking host : %s' %str(host))
                if re.search(host, url):
                    logger.log_debug('RealDebrid Match found')
                    return True
        elif host:
            if self.hosts is None:
                self.hosts = self.get_hosts()
                
            if host.startswith('www.'):
                host = host.replace('www.', '')
            if any(host in item for item in self.hosts):
                return True
        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_torrents" type="bool" label="%s" default="true"/>' % (cls.__name__, i18n('torrents')))
        xml.append('<setting id="%s_cached_only" enable="eq(-1,true)" type="bool" label="%s" default="false" />' % (cls.__name__, i18n('cached_only')))
        xml.append('<setting id="%s_autopick" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('auto_primary_link')))
        xml.append('<setting id="%s_auth" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_rd)"/>' % (cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="%s_reset" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_rd)"/>' % (cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="%s_token" visible="false" type="text" default=""/>' % cls.__name__)
        xml.append('<setting id="%s_refresh" visible="false" type="text" default=""/>' % cls.__name__)
        xml.append('<setting id="%s_client_id" visible="false" type="text" default=""/>' % cls.__name__)
        xml.append('<setting id="%s_client_secret" visible="false" type="text" default=""/>' % cls.__name__)
        return xml

    @classmethod
    def isUniversal(cls):
        return True
