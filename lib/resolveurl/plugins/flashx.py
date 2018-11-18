"""
flashx.tv resolveurl plugin
Copyright (C) 2017 jsergio

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
import urllib2
import json
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError


class FlashxResolver(ResolveUrl):
    name = "flashx"
    domains = ["flashx.tv", "flashx.to", "flashx.sx", "flashx.bz", "flashx.cc"]
    pattern = '(?://|\.)(flashx\.(?:tv|to|sx|cc|bz))/(?:embed-|dl\?|embed.php\?c=)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.RAND_UA}

    def get_media_url(self, host, media_id):
        result = self.__check_auth(media_id)
        if not result:
            result = self.__auth_ip(media_id)

        if result:
            return helpers.get_media_url(result, patterns=['''src:\s*["'](?P<url>[^"']+).+?res:\s*(?P<label>\d+)'''], result_blacklist=["trailer"], generic_patterns=False).replace(' ', '%20')

        raise ResolverError(i18n('no_ip_authorization'))

    def __auth_ip(self, media_id):
        header = i18n('flashx_auth_header')
        line1 = i18n('auth_required')
        line2 = i18n('visit_link')
        line3 = i18n('click_pair') % 'http://flashx.tv/pair'
        with common.kodi.CountdownDialog(header, line1, line2, line3, countdown=120) as cd:
            return cd.start(self.__check_auth, [media_id])

    def __check_auth(self, media_id):
        common.logger.log('Checking Auth: %s' % media_id)
        url = 'https://www.flashx.tv/pairing.php?c=paircheckjson'
        try:
            js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError:
            raise ResolverError('Unusable Authorization Response')
        except urllib2.HTTPError as e:
            if e.code == 401:
                js_result = json.loads(str(e.read()))
            else:
                raise

        common.logger.log('Auth Result: %s' % js_result)
        if js_result.get('status') == 'true':
            return self.resolve_url(media_id)
        else:
            return False

    def resolve_url(self, media_id):
        web_url = self.get_url('flashx.tv', media_id)
        html = self.net.http_GET(web_url, headers=self.headers).content

        if html:
            try:
                scripts = ['/code.js', '/counter.cgi']
                self.headers.update({'Referer': web_url})
                for match in re.finditer('''<script[^>]*src=["']([^'"]+)''', html):
                    url = 'http:%s' % match.group(1) if match.group(1).startswith('//') else match.group(1)
                    if any(i in url.lower() for i in scripts):
                        self.net.http_GET(url, headers=self.headers)
                self.net.http_GET('https://www.flashx.tv/flashx.php', headers=self.headers)
                playvid_url = re.search('''href=['"]([^"']+/playvideo-[^"']+)''', html)
                if playvid_url:
                    return playvid_url.group(1)

                raise ResolverError('Could not locate playvideo url')

            except Exception as e:
                raise ResolverError('Exception during flashx resolve parse: %s' % e)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.flashx.tv/embed.php?c={media_id}')

    @classmethod
    def isPopup(self):
        return True
