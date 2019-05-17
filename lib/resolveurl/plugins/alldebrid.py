"""
    resolveurl Kodi Addon

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
from urllib import quote_plus
from urllib2 import HTTPError
import json
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

AGENT = 'ResolveURL for Kodi'
VERSION = common.addon_version
USER_AGENT = '%s/%s' % (AGENT, VERSION)
FORMATS = common.VIDEO_FORMATS

api_url = 'https://api.alldebrid.com'


class AllDebridResolver(ResolveUrl):
    name = "AllDebrid"
    domains = ['*']

    def __init__(self):
        self.net = common.Net()
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id, cached_only=False):
        try:
            if media_id.lower().startswith('magnet:'):
                r = re.search('''magnet:.+?urn:([a-zA-Z0-9]+):([a-zA-Z0-9]+)''', media_id, re.I)
                if r:
                    _hash, _format = r.group(2), r.group(1)
                    if self.__check_cache(_hash):
                        logger.log_debug('AllDebrid: BTIH %s is readily available to stream' % _hash)
                        transfer_id = self.__create_transfer(_hash)
                    else:
                        if self.get_setting('cached_only') == 'true' or cached_only:
                            raise ResolverError('AllDebrid: Cached torrents only allowed to be initiated')
                        else:
                            transfer_id = self.__create_transfer(_hash)
                            self.__initiate_transfer(transfer_id)

                    transfer_info = self.__list_transfer(transfer_id)
                    for _link, _file in transfer_info.get('links').items():
                        if any(_file.lower().endswith(x) for x in FORMATS):
                            media_id = _link.replace("\/", "/")
                            break

                    self.__delete_transfer(transfer_id)

            url = '%s/link/unlock?agent=%s&version=%s&token=%s&link=%s' % (api_url, quote_plus(AGENT), quote_plus(VERSION), self.get_setting('token'), media_id)
            result = self.net.http_GET(url, headers=self.headers).content
        except HTTPError as e:
            try:
                js_result = json.loads(e.read())
                if 'error' in js_result:
                    msg = '%s (%s)' % (js_result.get('error'), js_result.get('errorCode'))
                else:
                    msg = 'Unknown Error (1)'
            except:
                msg = 'Unknown Error (2)'
            raise ResolverError('AllDebrid Error: %s (%s)' % (msg, e.code))
        else:
            js_result = json.loads(result)
            logger.log_debug('AllDebrid resolve: [%s]' % js_result)
            if 'error' in js_result:
                raise ResolverError('AllDebrid Error: %s (%s)' % (js_result.get('error'), js_result.get('errorCode')))
            elif js_result.get('success', False):
                if js_result.get('infos').get('link'):
                    return js_result.get('infos').get('link')

        raise ResolverError('AllDebrid: no stream returned')

    def __check_cache(self, media_id):
        try:
            url = '%s/magnet/instant?agent=%s&version=%s&token=%s&magnet=%s' % (api_url, quote_plus(AGENT), quote_plus(VERSION), self.get_setting('token'), media_id)
            result = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(result)
            if result.get('success', False):
                response = result.get('instant', False)
                return response
        except:
            pass

        return False

    def __list_transfer(self, transfer_id):
        try:
            url = '%s/magnet/status?agent=%s&version=%s&token=%s&id=%s' % (api_url, quote_plus(AGENT), quote_plus(VERSION), self.get_setting('token'), transfer_id)
            response = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(response)
            if result.get('success', False):
                return result
        except:
            pass

        return {}

    def __create_transfer(self, media_id):
        try:
            url = '%s/magnet/upload?agent=%s&version=%s&token=%s&magnet=%s' % (api_url, quote_plus(AGENT), quote_plus(VERSION), self.get_setting('token'), media_id)
            response = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(response)
            if result.get('success', False):
                logger.log_debug('Transfer successfully started to the AllDebrid cloud')
                return result.get('id', "")
        except:
            pass

        return ""

    def __initiate_transfer(self, transfer_id, interval=5):
        try:
            transfer_info = self.__list_transfer(transfer_id)
            if transfer_info:
                line1 = transfer_info.get('filename')
                line2 = 'Saving torrent to UptoBox via AllDebrid'
                line3 = transfer_info.get('status')
                with common.kodi.ProgressDialog('Resolve URL AllDebrid Transfer', line1, line2, line3) as pd:
                    while not transfer_info.get('statusCode') == 4:
                        common.kodi.sleep(1000 * interval)
                        transfer_info = self.__list_transfer(transfer_id)
                        file_size = transfer_info.get('size')
                        line1 = transfer_info.get('filename')
                        if transfer_info.get('statusCode') == 1:
                            download_speed = round(float(transfer_info.get('downloadSpeed')) / (1000**2), 2)
                            progress = int(float(transfer_info.get('downloaded')) / file_size * 100) if file_size > 0 else 0
                            line3 = "Downloading at %s MB/s from %s peers, %s%% of %sGB completed" % (download_speed, transfer_info.get('seeders'), progress, round(float(file_size) / (1000 ** 3), 2))
                        elif transfer_info.get('statusCode') == 3:
                            upload_speed = round(float(transfer_info.get('uploadSpeed')) / (1000 ** 2), 2)
                            progress = int(float(transfer_info.get('uploaded')) / file_size * 100) if file_size > 0 else 0
                            line3 = "Uploading at %s MB/s, %s%% of %s GB completed" % (upload_speed, progress, round(float(file_size) / (1000 ** 3), 2))
                        else:
                            line3 = transfer_info.get('status')
                            progress = 0
                        logger.log_debug(line3)
                        pd.update(progress, line1=line1, line3=line3)
                        if pd.is_canceled():
                            self.__delete_transfer(transfer_id)
                            # self.__delete_folder()
                            raise ResolverError('Transfer ID %s :: Canceled by user' % transfer_id)
                        elif 5 <= transfer_info.get('statusCode') <= 10:
                            self.__delete_transfer(transfer_id)
                            # self.__delete_folder()
                            raise ResolverError('Transfer ID %s :: %s' % (transfer_id, transfer_info.get('status')))

                common.kodi.sleep(1000 * interval)  # allow api time to generate the links

            return

        except Exception as e:
            self.__delete_transfer(transfer_id)
            raise ResolverError('Transfer ID %s :: %s' % (transfer_id, e))

    def __delete_transfer(self, transfer_id):
        try:
            url = '%s/magnet/delete?agent=%s&version=%s&token=%s&id=%s' % (api_url, quote_plus(AGENT), quote_plus(VERSION), self.get_setting('token'), transfer_id)
            response = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(response)
            if result.get('success', False):
                logger.log_debug('Transfer ID "%s" deleted from the AllDebrid cloud' % transfer_id)
                return True
        except:
            pass

        return False

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.alldebrid.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        hosters = []
        url = '%s/user/hosts?agent=%s&version=%s&token=%s' % (api_url, quote_plus(AGENT), quote_plus(VERSION), self.get_setting('token'))
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get('success', False):
                regexes = [value.get('regexp').replace('\/', '/') for key, value in js_data.get('hosts', {}).iteritems()
                           if value.get('status', False)]
                logger.log_debug('AllDebrid hosters : %s' % regexes)
                hosters = [re.compile(regex) for regex in regexes]
            else:
                logger.log_error('Error getting AD Hosters')
        except Exception as e:
            logger.log_error('Error getting AD Hosters: %s' % e)
        return hosters

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        url = '%s/hosts/domains' % api_url
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get('success', False):
                hosts = [host.replace('www.', '') for host in js_data.get('hosts', [])]
                if self.get_setting('torrents') == 'true':
                    hosts.extend([u'torrent', u'magnet'])
                logger.log_debug('AllDebrid hosts : %s' % hosts)
            else:
                logger.log_error('Error getting AD Hosters')
        except Exception as e:
            logger.log_error('Error getting AD Hosts: %s' % e)
        return hosts

    def valid_url(self, url, host):
        logger.log_debug('in valid_url %s : %s' % (url, host))
        if url:
            if url.lower().startswith('magnet:') and self.get_setting('torrents') == 'true':
                return True
            if self.hosters is None:
                self.hosters = self.get_all_hosters()

            for regexp in self.hosters:
                # logger.log_debug('AllDebrid checking host : %s' %str(regexp))
                if re.search(regexp, url):
                    logger.log_debug('AllDebrid Match found')
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

    def reset_authorization(self):
        self.set_setting('token', '')

    def authorize_resolver(self):
        url = '%s/pin/get?agent=%s&version=%s' % (api_url, quote_plus(AGENT), quote_plus(VERSION))
        js_result = self.net.http_GET(url, headers=self.headers).content
        js_data = json.loads(js_result)
        line1 = 'Go to URL: %s' % (js_data.get('base_url').replace('\/', '/'))
        line2 = 'When prompted enter: %s' % (js_data.get('pin'))
        with common.kodi.CountdownDialog('Resolve Url All Debrid Authorization', line1, line2,
                                         countdown=js_data.get('expired_in', 120)) as cd:
            result = cd.start(self.__check_auth, [js_data.get('check_url').replace('\/', '/')])

        # cancelled
        if result is None:
            return
        return self.__get_token(js_data.get('check_url').replace('\/', '/'))

    def __get_token(self, url):
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get("success", False):
                token = js_data.get('token', '')
                logger.log_debug('Authorizing All Debrid Result: |%s|' % token)
                self.set_setting('token', token)
                return True
        except Exception as e:
            logger.log_debug('All Debrid Authorization Failed: %s' % e)
            return False

    def __check_auth(self, url):
        activated = False
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get("success", False):
                activated = js_data.get('activated', False)
        except Exception as e:
            logger.log_debug('Exception during AD auth: %s' % e)
        return activated

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        # xml.append('<setting id="%s_autopick" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('auto_primary_link')))
        xml.append('<setting id="%s_torrents" type="bool" label="%s" default="true"/>' % (cls.__name__, i18n('torrents')))
        xml.append('<setting id="%s_cached_only" enable="eq(-1,true)" type="bool" label="%s" default="false" />' % (cls.__name__, i18n('cached_only')))
        xml.append('<setting id="%s_auth" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_ad)"/>' % (cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="%s_reset" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_ad)"/>' % (cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="%s_token" visible="false" type="text" default=""/>' % cls.__name__)
        return xml

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    @classmethod
    def isUniversal(self):
        return True
