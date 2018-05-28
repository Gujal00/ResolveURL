"""
    ResolveURL Addon for Kodi
    Copyright (C) 2016 t0mm0, tknorris

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
import hashlib
import time
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
try:
    from crypto.keyedHash.hmacHash import HMAC_SHA1
    from crypto.common import xor
except ImportError:
    HMAC_SHA1 = None
from math import ceil
from struct import pack
import binascii


def pbkdf2(password, salt, iterations, keySize, PRF=HMAC_SHA1):
    """ Create key of size keySize from password and salt """
    if len(password)>63:
        raise 'Password too long for pbkdf2'
    #if len(password)<8 : raise 'Password too short for pbkdf2'
    if (keySize > 10000):         # spec says >4294967295L*digestSize
        raise 'keySize too long for PBKDF2'

    prf = PRF(key=password)  # HMAC_SHA1
    numBlocks = int(ceil(1.*keySize/prf.digest_size)) # ceiling function
    key = ''
    for block in range(1,numBlocks+1):
        # Calculate F(P, salt, iterations, i)
        F = prf(salt+pack('>i',block)) # i is packed into 4 big-endian bytes
        U = prf(salt+pack('>i',block)) # i is packed into 4 big-endian bytes
        for count in range(2,iterations+1):
            U = prf(U)
            F = xor(F,U)
        key = key + F
    return key[:keySize]

def dot11PassPhraseToPSK(passPhrase,ssid):
    """ The 802.11 TGi recommended pass-phrase-to-preshared-key mapping.
        This function simply uses pbkdf2 with interations=4096 and keySize=32
    """
    assert(7<len(passPhrase)<64), 'Passphrase must be greater than 7 or less than 64 characters'
    return pbkdf2(passPhrase, ssid, iterations=4096, keySize=32)


CLIENT_ID = 'MUQMIQX6YWDSU'
USER_AGENT = 'ResolveURL for Kodi/%s' % (common.addon_version)
INTERVALS = 5

class SmoozedResolver(ResolveUrl):
    name = "SMOOZED"
    domains = ["*"]

    def __init__(self):
        self.net = common.Net()
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id, retry=False):
        try:
            url = 'https://www.smoozed.com/api/download'
            data = {'session_key': self.get_session_key(), 'url': media_id}
            result = self.net.http_POST(url, form_data=data, compression=False)
            return result.get_url()
        except urllib2.HTTPError as e:
            content = e.read()
            try:
                data = json.loads(content)
            except Exception:
                data = None
            print repr(content)
            print repr(data)
            if e.code == 403:
                self.set_setting('session_key', '')
            raise
        except Exception as e:
            raise ResolverError('Unexpected Exception during SMOOZED: %s' % (e))

    def get_session_key(self):
        session_key = self.get_setting('session_key')
        if not session_key:
            password = self.get_setting('password')
            salt = hashlib.sha256(password).hexdigest()
            encrypted = binascii.hexlify(pbkdf2(password, salt, 1000, 32))
            p = "auth="+self.get_setting('email')+"&password="+encrypted
            html = self.net.http_GET("https://www.smoozed.com/api/login?"+p).content
            data = json.loads(html)
            if data['state'] != 'ok':
                raise ResolverError('SMOOZED Auth Failed')
            if float(data['data']['user']['user_premium']) < time.time():
                if float(data['data']['user'].get('user_trial', 0)) < time.time():
                    raise ResolverError('SMOOZED Account Expired')
            session_key = data['data']['session_key']
            self.set_setting('session_key', session_key)
        return session_key

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.smoozed.com', url

    #@common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        hosters = []
        try:
            url = 'https://www.smoozed.com/api/hoster/regex'
            data = {'session_key': self.get_session_key()}
            js_result = json.loads(self.net.http_POST(url, form_data=data).content)
            regexes = [regex for regex in js_result["data"].values()]
            common.logger.log_debug('SMOOZED hosters : %s' % (regexes))
            hosters = [re.compile(regex) for regex in regexes]
        except Exception as e:
            common.logger.log_error('Error getting SMOOZED regexes: %s' % (e))
            raise
        return hosters

    @common.cache.cache_method(cache_limit=8)
    def get_hosts(self):
        hosts = []
        try:
            url = 'https://www.smoozed.com/api/hoster/regex'
            data = {'session_key': self.get_session_key()}
            js_result = json.loads(self.net.http_POST(url, form_data=data).content)
            hosts = js_result["data"].keys()
        except Exception as e:
            common.logger.log_error('Error getting SMOOZED hosts: %s' % (e))
        common.logger.log_debug('SMOOZED hosts : %s' % (hosts))
        return hosts

    @classmethod
    def _is_enabled(cls):
        if HMAC_SHA1 is None:
            return False
        return cls.get_setting('enabled') == 'true' and cls.get_setting('email')

    def valid_url(self, url, host):
        if HMAC_SHA1 is None:
            return False
        common.logger.log_debug('in valid_url %s : %s' % (url, host))
        if url:
            if self.hosters is None:
                self.hosters = self.get_all_hosters()
                
            for host in self.hosters:
                common.logger.log_debug('SMOOZED Checking Host : %s' %str(host))
                if re.search(host, url):
                    common.logger.log_debug('SMOOZED Match found')
                    return True
        elif host:
            if self.hosts is None:
                self.hosts = self.get_hosts()
                
            if host.startswith('www.'): host = host.replace('www.', '')
            if any(host in item for item in self.hosts):
                return True
        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_email" visible="true" type="text" label="Username" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_password" visible="true" type="text" label="Password" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_session_key" visible="false" type="text" default=""/>' % (cls.__name__))
        return xml

    @classmethod
    def isUniversal(self):
        return True
