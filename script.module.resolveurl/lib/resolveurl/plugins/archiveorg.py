"""
    Plugin for ResolveURL
    Copyright (c) 2023 gujal

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
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class ArchiveOrgResolver(ResolveUrl):
    name = 'Archive_Org'
    domains = ['archive.org']
    pattern = r'(?://|\.)(archive\.org)/(?:embed|details|download)/([0-9a-zA-Z-_\.]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        needs_login = re.search(r'''class="theatre-title">You\s*must\s*log\s*in''', html)

        if needs_login:
            username, password = self.get_setting('username'), self.get_setting('password')
            if not (username and password):
                raise ResolverError(self.name + ' username & password required')
            login_url = 'https://archive.org/services/account/login/'
            resp = self.net.http_GET(login_url, headers=headers).json
            token = resp.get('value').get('token')
            data = {
                'username': username,
                'password': password,
                't': token
            }
            try:
                resp = self.net.http_POST(login_url, form_data=data, headers=headers, jdata=True)
                cookie = resp.get_cookies()
                if cookie:
                    headers.update({'Cookie': cookie})
                html = self.net.http_GET(web_url, headers=headers).content
            except:
                raise ResolverError('Login unsuccessful')

        sources = re.findall(r'"file":"(?P<url>[^"]+)[^}]+?label":"(?P<label>[\d]+p?)', html)
        if sources:
            sources = [(x[1], x[0]) for x in sources]
            surl = 'https://' + host + helpers.pick_source(helpers.sort_sources_list(sources)).replace('/download/', '/serve/').replace(' ', '%20')
            return surl + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml(include_login=False)
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="%s" default=""/>' % (cls.__name__, i18n('username')))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="%s" option="hidden" default=""/>' % (cls.__name__, i18n('password')))
        return xml
