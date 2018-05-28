# -*- coding: utf-8 -*-
"""
    Purevid resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0, belese, JUL1EN094

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

import os
import re
import urllib
import json
from resolveurl import common
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError  # @UnusedImport

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

class PureVidResolver(ResolveUrl):
    name = "purevid"
    domains = ["purevid.com"]
    pattern = '(?://|\.)(purevid\.com)/v/([0-9A-Za-z]+)'

    profile_path = common.profile_path
    pv_cookie_file = os.path.join(profile_path, '%s.cookies' % name)

    def __init__(self):
        self.net = common.Net()
        try: os.makedirs(os.path.dirname(self.pv_cookie_file))
        except OSError: pass

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        data = json.loads(html)
        if self.get_setting('quality') == 'FLV':
            url = data['clip']['bitrates'][0]['url']
        else:
            url = data['clip']['bitrates'][-1]['url']
        params = ''
        for val in data['plugins']['lighttpd']['params']:
            params += val['name'] + '=' + val['value'] + '&'
        url = url + '?' + params[:-1]
        cookies = {}
        for cookie in self.net._cj:
            cookies[cookie.name] = cookie.value
        url += helpers.append_headers({'Cookie': urllib.urlencode(cookies)})
        logger.log_debug(url)
        return url

    def get_url(self, host, media_id):
        return 'http://www.purevid.com/?m=video_info_embed_flv&id=%s' % media_id

    def needLogin(self):
        url = 'http://www.purevid.com/?m=main'
        if not os.path.exists(self.pv_cookie_file):
            return True
        self.net.set_cookies(self.pv_cookie_file)
        source = self.net.http_GET(url).content
        logger.log_debug(source.encode('utf-8'))
        if re.search("""<span>Welcome <strong>.*</strong></span>""", source):
            logger.log_debug('needLogin returning False')
            return False
        else:
            logger.log_debug('needLogin returning True')
            return True

    def login(self):
        if self.needLogin():
            logger.log('login to purevid')
            url = 'http://www.purevid.com/?m=login'
            data = {'username': self.get_setting('username'), 'password': self.get_setting('password')}
            source = self.net.http_POST(url, data).content
            if re.search(self.get_setting('username'), source):
                self.net.save_cookies(self.pv_cookie_file)
                self.net.set_cookies(self.pv_cookie_file)
                return True
            else:
                return False
        else:
            return True

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="login" default="false"/>' % (cls.__name__))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="Username" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="Password" option="hidden" default=""/>' % (cls.__name__))
        xml.append('<setting label="Video quality" id="%s_quality" type="labelenum" values="FLV|Maximum" default="Maximum" />' % (cls.__name__))
        xml.append('<setting label="This plugin calls the Purevid resolveurl - change settings there." type="lsep" />')
        return xml
