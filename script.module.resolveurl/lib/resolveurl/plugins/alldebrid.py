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
from six.moves import urllib_parse, urllib_error
import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

AGENT = 'ResolveURL for Kodi'
VERSION = common.addon_version
USER_AGENT = '{0}/{1}'.format(AGENT, VERSION)
FORMATS = common.VIDEO_FORMATS

api_url = 'https://api.alldebrid.com/v4'


class AllDebridResolver(ResolveUrl):
    name = 'AllDebrid'
    domains = ['*']

    def __init__(self):
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id, cached_only=False, return_all=False):
        try:
            if media_id.lower().startswith('magnet:'):
                r = re.search('''magnet:.+?urn:([a-zA-Z0-9]+):([a-zA-Z0-9]+)''', media_id, re.I)
                if r:
                    _hash = r.group(2)
                    if self.__check_cache(_hash):
                        logger.log_debug('AllDebrid: BTIH {0} is readily available to stream'.format(_hash))
                        transfer_id = self.__create_transfer(_hash)
                    else:
                        if self.get_setting('cached_only') == 'true' or cached_only:
                            raise ResolverError('AllDebrid: {0}'.format(i18n('cached_torrents_only')))
                        else:
                            transfer_id = self.__create_transfer(_hash)
                            self.__initiate_transfer(transfer_id)

                    transfer_info = self.__list_transfer(transfer_id)
                    if return_all:
                        sources = [{'name': link.get('filename').split('/')[-1], 'link': link.get('link')}
                                   for link in transfer_info.get('links')
                                   if any(link.get('filename').lower().endswith(x) for x in FORMATS)]
                        return sources
                    else:
                        sources = [(link.get('size'), link.get('link'))
                                   for link in transfer_info.get('links')
                                   if any(link.get('filename').lower().endswith(x) for x in FORMATS)]
                        media_id = max(sources)[1]
                        self.__delete_transfer(transfer_id)

            url = '{0}/link/unlock?agent={1}&apikey={2}&link={3}'.format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'), urllib_parse.quote_plus(media_id))
            result = self.net.http_GET(url, headers=self.headers).content
        except urllib_error.HTTPError as e:
            try:
                js_result = json.loads(e.read())
                if 'error' in js_result:
                    msg = '{0} ({1})'.format(js_result.get('error'), js_result.get('errorCode'))
                else:
                    msg = 'Unknown Error (1)'
            except:
                msg = 'Unknown Error (2)'
            raise ResolverError('AllDebrid Error: {0} ({1})'.format(msg, e.code))
        else:
            js_result = json.loads(result)
            logger.log_debug('AllDebrid resolve: [{0}]'.format(js_result))
            if 'error' in js_result:
                e = js_result.get('error')
                raise ResolverError('AllDebrid Error: {0} ({1})'.format(e.get('message'), e.get('code')))
            elif js_result.get('status', False) == "success":
                if js_result.get('data').get('link'):
                    return js_result.get('data').get('link')
                elif js_result.get('data').get('host') == "stream":
                    sources = js_result.get('data').get('streams')
                    fid = js_result.get('data').get('id')
                    sources = [(str(source.get("quality")), source.get("id")) for source in sources if '+' not in source.get("id")]
                    sid = helpers.pick_source(helpers.sort_sources_list(sources))
                    url = '{0}/link/streaming?agent={1}&apikey={2}&id={3}&stream={4}' \
                          .format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'), fid, sid)
                    result = self.net.http_GET(url, headers=self.headers).content
                    js_data = json.loads(result)
                    if js_data.get('data').get('link'):
                        return js_data.get('data').get('link')

        raise ResolverError('AllDebrid: {0}'.format(i18n('no_stream')))

    def __check_cache(self, media_id):
        url = '{0}/magnet/instant?agent={1}&apikey={2}&magnets[]={3}'.format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'), media_id.lower())
        result = self.net.http_GET(url, headers=self.headers).content
        result = json.loads(result)
        if result.get('status') == "success":
            magnets = result.get('data').get('magnets')
            for magnet in magnets:
                if media_id.lower() == magnet.get('magnet').lower() or media_id.lower() == magnet.get('hash').lower():
                    response = magnet.get('instant', False)
                    return response
        else:
            ecode = result.get('error', {}).get('code', '')
            if ecode == "AUTH_BLOCKED":
                logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                raise ResolverError(i18n('validate'))
            elif ecode == "AUTH_USER_BANNED":
                logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                raise ResolverError(i18n('banned'))
            return False

    def __list_transfer(self, transfer_id):
        url = '{0}/magnet/status?agent={1}&apikey={2}&id={3}'.format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'), transfer_id)
        result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        if result.get('status', False) == "success":
            magnets = result.get('data').get('magnets')
            if type(magnets) is list:
                for magnet in magnets:
                    if transfer_id == magnet.get('id'):
                        return magnet
            else:
                return magnets
        else:
            ecode = result.get('error', {}).get('code', '')
            if ecode == "AUTH_BLOCKED":
                logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                raise ResolverError(i18n('validate'))
            elif ecode == "AUTH_USER_BANNED":
                logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                raise ResolverError(i18n('banned'))
            return {}

    def __create_transfer(self, media_id):
        url = '{0}/magnet/upload?agent={1}&apikey={2}&magnets[]={3}'.format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'), media_id)
        result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        if result.get('status', False) == "success":
            logger.log_debug('Transfer successfully started to the AllDebrid cloud')
            magnets = result.get('data').get('magnets')
            for magnet in magnets:
                if media_id in magnet.get('magnet') or media_id.lower() == magnet.get('hash').lower():
                    return magnet.get('id')
        else:
            ecode = result.get('error', {}).get('code', '')
            if ecode == "AUTH_BLOCKED":
                logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                raise ResolverError(i18n('validate'))
            elif ecode == "AUTH_USER_BANNED":
                logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                raise ResolverError(i18n('banned'))
            return ''

    def __initiate_transfer(self, transfer_id, interval=5):
        try:
            transfer_info = self.__list_transfer(transfer_id)
            if transfer_info:
                line1 = transfer_info.get('filename')
                line2 = i18n('ad_uptobox')
                line3 = transfer_info.get('status')
                with common.kodi.ProgressDialog('ResolveURL AllDebrid {0}'.format(i18n('transfer')), line1, line2, line3) as pd:
                    while not transfer_info.get('statusCode') == 4:
                        common.kodi.sleep(1000 * interval)
                        transfer_info = self.__list_transfer(transfer_id)
                        file_size = transfer_info.get('size')
                        file_size2 = round(float(file_size) / (1000 ** 3), 2)
                        line1 = transfer_info.get('filename')
                        if transfer_info.get('statusCode') == 1:
                            download_speed = round(float(transfer_info.get('downloadSpeed')) / (1000**2), 2)
                            progress = int(float(transfer_info.get('downloaded')) / file_size * 100) if file_size > 0 else 0
                            line3 = "{0} {1}MB/s from {2} peers, {3}% {4} {5}GB {6}".format(
                                i18n('downloading'), download_speed, transfer_info.get('seeders'), progress,
                                i18n('of'), file_size2, i18n('completed')
                            )
                        elif transfer_info.get('statusCode') == 3:
                            upload_speed = round(float(transfer_info.get('uploadSpeed')) / (1000 ** 2), 2)
                            progress = int(float(transfer_info.get('uploaded')) / file_size * 100) if file_size > 0 else 0
                            line3 = "{0} {1}MB/s, {2}% {3} {4}GB {5}".format(
                                i18n('uploading'), upload_speed, progress, i18n('of'),
                                file_size2, i18n('completed')
                            )
                        else:
                            line3 = transfer_info.get('status')
                            progress = 0
                        logger.log_debug(line3)
                        pd.update(progress, line1=line1, line3=line3)
                        if pd.is_canceled():
                            keep_transfer = common.kodi.yesnoDialog(
                                heading='ResolveURL AllDebrid {0}'.format(i18n('transfer')),
                                line1=i18n('ad_background')
                            )
                            if not keep_transfer:
                                self.__delete_transfer(transfer_id)
                            raise ResolverError('{0} ID {1} :: {2}'.format(i18n('transfer'), transfer_id, i18n('user_cancelled')))
                        elif 5 <= transfer_info.get('statusCode') <= 10:
                            self.__delete_transfer(transfer_id)
                            raise ResolverError('{0} ID {1} :: {2}'.format(i18n('transfer'), transfer_id, transfer_info.get('status')))

                common.kodi.sleep(1000 * interval)  # allow api time to generate the links

            return

        except Exception as e:
            self.__delete_transfer(transfer_id)
            raise ResolverError('Transfer ID {0} :: {1}'.format(transfer_id, e))

    def __delete_transfer(self, transfer_id):
        try:
            url = '{0}/magnet/delete?agent={1}&apikey={2}&id={3}'.format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'), transfer_id)
            response = self.net.http_GET(url, headers=self.headers).content
            result = json.loads(response)
            if result.get('status', False) == "success":
                if 'deleted' in response.get('data').get('message'):
                    logger.log_debug('Transfer ID "{0}" deleted from AllDebrid cloud'.format(transfer_id))
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
        url = '{0}/user/hosts?agent={1}&apikey={2}'.format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'))
        try:
            result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(result)
            if js_data.get('status', False) == "success":
                js_data = js_data.get('data')
                regexes = [value.get('regexp') for _, value in js_data.get('hosts', {}).items()
                           if value.get('status', False)]
                hosters = [re.compile(regex) for regex in regexes]
                logger.log_debug('AllDebrid hosters : {0}'.format(len(hosters)))
                regexes = [value.get('regexp') for _, value in js_data.get('streams', {}).items()]
                streamers = []
                for regex in regexes:
                    try:
                        streamers.append(re.compile(regex))
                    except:
                        pass
                logger.log_debug('AllDebrid Streamers : {0}'.format(len(streamers)))
                hosters.extend(streamers)
                logger.log_debug('AllDebrid Total hosters : {0}'.format(len(hosters)))
            else:
                logger.log_error('Error getting AD Hosters')
        except Exception as e:
            logger.log_error('Error getting AD Hosters: {0}'.format(e))
        return hosters

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        url = '{0}/hosts/domains?agent={1}&apikey={2}'.format(api_url, urllib_parse.quote_plus(AGENT), self.get_setting('token'))
        try:
            js_result = self.net.http_GET(url, headers=self.headers).content
            js_data = json.loads(js_result)
            if js_data.get('status', False) == "success":
                # hosts = [host.replace('www.', '') for host in js_data.get('hosts', [])]
                hosts = js_data.get('data').get('hosts')
                hosts.extend(js_data.get('data').get('streams'))
                if self.get_setting('torrents') == 'true':
                    hosts.extend(['torrent', 'magnet'])
                logger.log_debug('AllDebrid hosts : {0}'.format(hosts))
            else:
                logger.log_error('Error getting AD Hosts')
        except Exception as e:
            logger.log_error('Error getting AD Hosts: {0}'.format(e))
        return hosts

    def valid_url(self, url, host):
        logger.log_debug('in valid_url {0} : {1}'.format(url, host))
        if url:
            if url.lower().startswith('magnet:') and self.get_setting('torrents') == 'true':
                return True
            if self.hosters is None:
                self.hosters = self.get_all_hosters()

            for regexp in self.hosters:
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
        url = '{0}/pin/get?agent={1}'.format(api_url, urllib_parse.quote_plus(AGENT))
        js_result = self.net.http_GET(url, headers=self.headers).content
        js_data = json.loads(js_result).get('data')
        line1 = '{0}: {1}'.format(i18n('goto_url'), js_data.get('base_url'))
        line2 = '{0}: {1}'.format(i18n('enter_prompt'), js_data.get('pin'))
        with common.kodi.CountdownDialog(
            'ResolveUrl AllDebrid {0}'.format(i18n('authorisation')), line1, line2,
            countdown=js_data.get('expires_in', 120)
        ) as cd:
            result = cd.start(self.__check_auth, [js_data.get('check_url')])

        # cancelled
        if result is None:
            return
        return self.__get_token(js_data.get('check_url'))

    def __get_token(self, url):
        try:
            js_data = json.loads(self.net.http_GET(url, headers=self.headers).content)
            if js_data.get("status", False) == "success":
                js_data = js_data.get('data')
                token = js_data.get('apikey', '')
                logger.log_debug('Authorizing All Debrid Result: |{0}|'.format(token))
                self.set_setting('token', token)
                return True
        except Exception as e:
            logger.log_debug('All Debrid Authorization Failed: {0}'.format(e))
            return False

    def __check_auth(self, url):
        activated = False
        try:
            js_data = json.loads(self.net.http_GET(url, headers=self.headers).content)
            if js_data.get("status", False) == "success":
                js_data = js_data.get('data')
                activated = js_data.get('activated', False)
            else:
                ecode = js_data.get('error', {}).get('code', '')
                if ecode == "AUTH_BLOCKED":
                    logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                    raise ResolverError(i18n('validate'))
                elif ecode == "AUTH_USER_BANNED":
                    logger.log_debug('Exception during AD auth: {0}'.format(ecode))
                    raise ResolverError(i18n('banned'))
        except Exception as e:
            logger.log_debug('Exception during AD auth: {0}'.format(e))
        return activated

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="{0}_torrents" type="bool" label="{1}" default="true"/>'.format(cls.__name__, i18n('torrents')))
        xml.append('<setting id="{0}_cached_only" enable="eq(-1,true)" type="bool" label="{1}" default="false" />'.format(cls.__name__, i18n('cached_only')))
        xml.append('<setting id="{0}_auth" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_ad)"/>'.format(cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="{0}_reset" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_ad)"/>'.format(cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="{0}_token" visible="false" type="text" default=""/>'.format(cls.__name__))
        return xml

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    @classmethod
    def isUniversal(cls):
        return True
