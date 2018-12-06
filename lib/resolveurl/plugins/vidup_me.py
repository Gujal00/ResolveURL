"""
    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
import urllib
import urllib2
from resolveurl import common
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VidUpMeResolver(ResolveUrl):
    name = "vidup.me"
    domains = ["vidup.me", "vidup.tv"]
    pattern = '(?://|\.)(vidup\.(?:me|tv))/(?:embed-|download/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.CHROME_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.parse_sources_list(html)
        if sources:
            try:
                token = re.search('''var thief\s*=\s*["']([^"']+)''', html)
                if token:
                    vt_url = 'http://vidup.tv/jwv/%s' % token.group(1)
                    vt_html = self.net.http_GET(vt_url, headers=headers).content
                    vt = re.search('''\|([-\w]{50,})''', vt_html)
                    if vt:
                        sources = helpers.sort_sources_list(sources)
                        params = {'direct': 'false', 'ua': 1, 'vt': vt.group(1)}
                        return helpers.pick_source(sources) + '?' + urllib.urlencode(params) + helpers.append_headers(headers)
                    else:
                        raise ResolverError('Video VT Missing')
                else:
                    raise ResolverError('Video Token Missing')
            except urllib2.HTTPError:
                raise ResolverError('Unable to read page data')

        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidup.tv/embed-{media_id}.html')
