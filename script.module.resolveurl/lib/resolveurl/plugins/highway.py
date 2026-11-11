"""
    Plugin for ResolveURL
    Copyright (C) 2026 Yaknar

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

import json
import re

from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolverError, ResolveUrl
from six.moves import urllib_error, urllib_parse

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

AGENT = 'ResolveURL for Kodi'
VERSION = common.addon_version
USER_AGENT = '{0}/{1}'.format(AGENT, VERSION)
FORMATS = common.VIDEO_FORMATS

SITE_URL = 'https://cloud.high-way.me/'
API_URL = SITE_URL + 'center-api/'


class HighWayResolver(ResolveUrl):
    name = 'High-Way'
    domains = ['*']

    def __init__(self):
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT, 'Accept': 'application/json'}
        self.token = self.get_setting('token')
        if self.token:
            self.headers.update({'Authorization': 'Bearer {0}'.format(self.token)})

    def __api(self, endpoint, query=None, data=None):
        """
        Calls the High-Way Download Center API. Errors come back as JSON {"error": ..., "message": ...}
        with a 4xx/5xx status; they are returned like any other answer.
        """
        url = API_URL + endpoint
        if query:
            url += '?' + urllib_parse.urlencode(query)
        try:
            if data is not None:
                content = self.net.http_POST(url, form_data=data, headers=self.headers, timeout=60).content
            else:
                content = self.net.http_GET(url, headers=self.headers, timeout=60).content
        except urllib_error.HTTPError as e:
            if e.code == 429:
                common.kodi.sleep(2000)
                return self.__api(endpoint, query, data)
            content = e.read()
        try:
            return json.loads(content)
        except (TypeError, ValueError):
            return {'error': 'invalid_response', 'message': 'Invalid answer from High-Way'}

    def __check_error(self, result):
        if result.get('error'):
            raise ResolverError('High-Way: {0}'.format(result.get('message') or result.get('error')))

    # hoster links: High-Way loads the file into its cache, then returns a direct link
    def __get_media_url_hoster(self, media_id):
        result = self.__api('download.php', data={'links': media_id})
        self.__check_error(result)
        results = result.get('results') or [{}]
        result = results[0]
        if int(result.get('code', 1)) != 0:
            raise ResolverError('High-Way: {0}'.format(result.get('message') or i18n('no_stream')))
        if result.get('queued'):
            raise ResolverError('High-Way: {0}'.format(result.get('message')))

        if not result.get('cache_ready'):
            # The cache download only continues while someone asks for it, so there is no background option
            with common.kodi.ProgressDialog('ResolveURL High-Way {0}'.format(i18n('transfer')), result.get('name') or '') as pd:
                ready = False
                while not ready:
                    if pd.is_canceled():
                        raise ResolverError('High-Way: {0}'.format(i18n('user_cancelled')))
                    common.kodi.sleep(1000 * max(2, min(int(result.get('retry_in_seconds') or 5), 10)))
                    status = self.__api('download.php', {'action': 'cache', 'id': result.get('id')})
                    self.__check_error(status)
                    if int(status.get('code', 1)) != 0:
                        raise ResolverError('High-Way: {0}'.format(status.get('message') or i18n('no_stream')))
                    ready = status.get('ready')
                    pd.update(int(status.get('percentage') or 0), line1=result.get('name') or '')
                    result['retry_in_seconds'] = status.get('retry_in_seconds')

        if not result.get('download'):
            raise ResolverError('High-Way: {0}'.format(i18n('no_stream')))
        return result.get('download')

    # torrents
    def __get_hash(self, magnet):
        r = re.search(r'''urn:btih:([a-z0-9]+)''', magnet, re.I)
        return r.group(1).lower() if r else None

    def __get_transfer(self, transfer_id, btih):
        transfer = self.__api('transfers.php', {'id': transfer_id, 'service': 'torrent'})
        if transfer.get('error') == 'not_found' and btih:
            # Queued transfers get a numeric id once they start; find them by hash
            listing = self.__api('transfers.php', {'service': 'torrent'})
            for item in listing.get('transfers') or []:
                if (item.get('hash') or '').lower() == btih:
                    return item
        return transfer

    def __get_media_url_torrent(self, media_id, cached_only, return_all):
        file_ref = None
        r = re.match(r'''hw:([^:|]+):([0-9a-f]+)\|(.+)''', media_id, re.I)
        if r:
            file_ref = (r.group(1), r.group(2))
            media_id = r.group(3)
        btih = self.__get_hash(media_id)

        if file_ref is None:
            check = self.__api('transfers.php', {'service': 'torrent', 'check': btih or media_id})
            self.__check_error(check)
            cached = any(item.get('ready') for item in (check.get('results') or {}).values())
            if not cached and (cached_only or self.get_setting('cached_only') == 'true'):
                raise ResolverError('High-Way: {0}'.format(i18n('cached_torrents_only')))

            added = self.__api('transfers.php', data={'magnet': media_id})
            self.__check_error(added)
            transfer = self.__get_transfer(added.get('id'), btih)
            self.__check_error(transfer)

            if transfer.get('state') != 'completed':
                with common.kodi.ProgressDialog('ResolveURL High-Way {0}'.format(i18n('transfer')), transfer.get('name') or '') as pd:
                    while transfer.get('state') != 'completed':
                        if transfer.get('state') == 'error':
                            raise ResolverError('High-Way: {0}'.format(i18n('no_stream')))
                        if pd.is_canceled():
                            # The transfer stays in the High-Way cloud and finishes there (the Kodi session
                            # may add and read torrents, not remove them)
                            raise ResolverError('High-Way: {0}'.format(i18n('user_cancelled')))
                        pd.update(int(transfer.get('progress') or 0), line1=transfer.get('name') or '', line2=transfer.get('state') or '')
                        common.kodi.sleep(5000)
                        transfer = self.__get_transfer(transfer.get('id'), btih)
                        self.__check_error(transfer)

            files = [
                f for f in transfer.get('files') or []
                if not f.get('partial') and any(f.get('path', '').lower().endswith(x) for x in FORMATS)
            ]
            if not files:
                raise ResolverError('High-Way: {0}'.format(i18n('no_stream')))

            if return_all:
                return [
                    {'name': f.get('path', '').split('/')[-1], 'link': 'hw:{0}:{1}|{2}'.format(transfer.get('id'), f.get('id'), media_id)}
                    for f in files
                ]
            file_ref = (transfer.get('id'), max(files, key=lambda f: f.get('size') or 0).get('id'))

        # A fresh signed link for the chosen file
        result = self.__api('transfers.php', {'id': file_ref[0], 'service': 'torrent', 'file': file_ref[1]})
        self.__check_error(result)
        link = (result.get('file') or {}).get('download_url')
        if not link:
            raise ResolverError('High-Way: {0}'.format(i18n('no_stream')))
        return link

    def get_media_url(self, host, media_id, cached_only=False, return_all=False):
        if media_id.lower().startswith('magnet:') or media_id.startswith('hw:'):
            return self.__get_media_url_torrent(media_id, cached_only, return_all)
        return self.__get_media_url_hoster(media_id)

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'high-way.me', url

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        try:
            js_data = self.__api('status.php')
            for item in js_data.get('items') or []:
                if item.get('is_hoster') != 1 or not item.get('available') or not item.get('enabled'):
                    continue
                # `code` is the main domain, `link_wildcards` lists more domains as *://domain/*|*://other/*
                hosts.append(item.get('code', '').lower())
                for wildcard in (item.get('link_wildcards') or '').split('|'):
                    r = re.match(r'''(?:\*|https?)://(?:\*\.)?([^/*]+)''', wildcard.strip())
                    if r:
                        hosts.append(r.group(1).lower())
            hosts = [h for h in set(hosts) if h]
            logger.log_debug('High-Way hosts : {0}'.format(hosts))
        except Exception as e:
            logger.log_error('Error getting High-Way hosts: {0}'.format(e))
        return hosts

    def valid_url(self, url, host):
        if url:
            if url.startswith('hw:'):
                return True
            if url.lower().startswith('magnet:'):
                return self.get_setting('torrents') == 'true'
            host = urllib_parse.urlsplit(url).netloc
        if not host:
            return False

        if self.hosts is None:
            self.hosts = self.get_hosts()

        host = host.lower().split(':')[0]
        if host.startswith('www.'):
            host = host[4:]
        return any(host == item or host.endswith('.' + item) for item in self.hosts)

    # SiteAuth methods
    def login(self):
        if not self.get_setting('token'):
            self.authorize_resolver()

    def reset_authorization(self):
        if self.token:
            # End the session on High-Way as well, so it disappears from the account's session list
            self.__api('sessions.php', data={'action': 'revoke'})
        if 'Authorization' in self.headers.keys():
            self.headers.pop('Authorization')
        self.token = ''
        self.set_setting('token', '')
        self.set_setting('user', '')

    def authorize_resolver(self):
        js_data = self.__api('device-auth.php', data={'action': 'link', 'client': 'kodi'})
        code = js_data.get('code')
        if not code:
            raise ResolverError('High-Way: {0}'.format(i18n('auth_fail')))
        line1 = '{0}: {1}'.format(i18n('goto_url'), SITE_URL + '#sessions')
        line2 = '{0}: {1}'.format(i18n('enter_prompt'), code)
        qr_file = common.make_qr_file('{0}?device_code={1}#sessions'.format(SITE_URL, code))
        with common.kodi.AuthProgressDialog(
            'ResolveUrl High-Way {0}'.format(i18n('authorisation')), line1, line2,
            image=qr_file, countdown=900
        ) as cd:
            result = cd.start(self.__check_auth, [code])

        # cancelled or expired
        if not result:
            return False
        return self.__get_info()

    def __check_auth(self, code):
        try:
            js_data = self.__api('device-auth.php', data={'action': 'link', 'code': code})
            if js_data.get('status') == 'linked' and js_data.get('session_id'):
                self.token = js_data.get('session_id')
                return True
        except Exception as e:
            logger.log_debug('Exception during High-Way auth: {0}'.format(e))
        return False

    def __get_info(self):
        self.headers.update({'Authorization': 'Bearer {0}'.format(self.token)})
        js_data = self.__api('transfers.php', {'stats': 1})
        if js_data.get('username'):
            self.set_setting('token', self.token)
            self.set_setting('user', js_data.get('username'))
            return True
        logger.log_debug('High-Way Authorization Failed: {0}'.format(js_data.get('message')))
        self.token = ''
        self.headers.pop('Authorization')
        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="{0}_torrents" type="bool" label="{1}" default="true"/>'.format(cls.__name__, i18n('torrents')))
        xml.append('<setting id="{0}_cached_only" enable="eq(-1,true)" type="bool" label="{1}" default="false" />'.format(cls.__name__, i18n('cached_only')))
        xml.append('<setting id="{0}_auth" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_hw)"/>'.format(cls.__name__, i18n('auth_my_account')))
        xml.append('<setting id="{0}_reset" type="action" label="{1}" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_hw)"/>'.format(cls.__name__, i18n('reset_my_auth')))
        xml.append('<setting id="{0}_user" enable="false" label="{1}" visible="eq(-4,true)" type="text" default=""/>'.format(cls.__name__, i18n('username')))
        xml.append('<setting id="{0}_token" visible="false" type="text" default=""/>'.format(cls.__name__))
        return xml

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and cls.get_setting('token')

    @classmethod
    def isUniversal(cls):
        return True
