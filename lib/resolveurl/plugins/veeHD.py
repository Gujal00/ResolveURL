"""
resolveurl XBMC Addon
Copyright (C) 2011 t0mm0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
import os
import urllib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VeeHDResolver(ResolveUrl):
    name = "VeeHD"
    domains = ["veehd.com"]
    pattern = '(?://|\.)(veehd\.com)/video/([0-9A-Za-z]+)'

    profile_path = common.profile_path
    cookie_file = os.path.join(profile_path, '%s.cookies' % name)

    def __init__(self):
        self.net = common.Net()
        try: os.makedirs(os.path.dirname(self.cookie_file))
        except OSError: pass

    # ResolveUrl methods
    def get_media_url(self, host, media_id):
        if not self.get_setting('login') == 'true' or not (self.get_setting('username') and self.get_setting('password')):
            raise ResolverError('VeeHD requires a username & password')

        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        # two possible playeriframe's: stream and download
        for match in re.finditer('playeriframe.+?src\s*:\s*"([^"]+)', html):
            player_url = 'http://%s%s' % (host, match.group(1))
            html = self.net.http_GET(player_url).content

            # if the player html contains an iframe the iframe url has to be gotten and then the player_url tried again
            r = re.search('<iframe.*?src="([^"]+)', html)
            if r:
                frame_url = 'http://%s%s' % (host, r.group(1))
                self.net.http_GET(frame_url)
                html = self.net.http_GET(player_url).content

            patterns = ['"video/divx"\s+src="([^"]+)', '"url"\s*:\s*"([^"]+)', 'href="([^"]+(?:mp4|avi))']
            for pattern in patterns:
                r = re.search(pattern, html)
                if r:
                    stream_url = urllib.unquote(r.group(1))
                    return stream_url

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return 'http://veehd.com/video/%s' % media_id

    # SiteAuth methods
    def login(self):
        loginurl = 'http://veehd.com/login'
        ref = 'http://veehd.com/'
        submit = 'Login'
        login = self.get_setting('username')
        pword = self.get_setting('password')
        terms = 'on'
        remember = 'on'
        data = {'ref': ref, 'uname': login, 'pword': pword, 'submit': submit, 'terms': terms, 'remember_me': remember}
        html = self.net.http_POST(loginurl, data).content
        self.net.save_cookies(self.cookie_file)
        if re.search('my dashboard', html):
            return True
        else:
            return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_login" type="bool" label="login" default="false"/>' % (cls.__name__))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="Username" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="Password" option="hidden" default=""/>' % (cls.__name__))
        return xml
