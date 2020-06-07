"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError


class UpToBoxResolver(ResolveUrl):
    name = "uptobox"
    domains = ["uptobox.com", "uptostream.com"]
    pattern = r'(?://|\.)(uptobox.com|uptostream.com)/(?:iframe/)?([0-9A-Za-z_]+)'

    def __init__(self):
        self.headers = {'User-Agent': common.RAND_UA}

    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        js_data = json.loads(self.net.http_GET(url, headers=self.headers).content)
        if js_data.get('message') == 'Success':
            js_data = js_data.get('data')
            heading = i18n('uptobox_auth_header')
            line1 = i18n('auth_required')
            line2 = i18n('upto_link').format(js_data.get('base_url'))
            line3 = i18n('upto_pair').format(js_data.get('pin'))
            with common.kodi.CountdownDialog(heading, line1, line2, line3, True, js_data.get('expired_in'), 10) as cd:
                js_result = cd.start(self.__check_auth, [js_data.get('check_url')])
            if js_result:
                js_result = js_result.get('data').get('streamLinks')
                sources = [(key, list(js_result.get(key).values())[0]) for key in list(js_result.keys())]
                return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(self.headers)

        raise ResolverError('The requested video was not found or may have been removed.')

    def __check_auth(self, url):
        try:
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError:
            raise ResolverError('Unusable Authorization Response')

        if js_result.get('statusCode') == 0:
            if js_result.get('data') == "wait-pin-validation":
                return False
            else:
                return js_result

        raise ResolverError('The requested video was not found or may have been removed.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://uptobox.com/api/streaming?file_code={media_id}')

    @classmethod
    def isPopup(self):
        return True
