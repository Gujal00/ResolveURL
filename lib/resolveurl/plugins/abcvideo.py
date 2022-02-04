"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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

from six.moves import urllib_parse
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class ABCVideoResolver(ResolveUrl):
    name = "abcvideo"
    domains = ['abcvideo.cc']
    pattern = r'(?://|\.)(abcvideo\.cc)/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        surl = 'https://abcvideo.cc/dl'
        domain = 'aHR0cHM6Ly9hYmN2aWRlby5jYzo0NDM.'
        web_url = self.get_url(host, media_id)
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers).content
        token = helpers.girc(html, rurl, domain)
        if token:
            data = {'op': 'video_src',
                    'file_code': media_id,
                    'g-recaptcha-response': token}
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            shtml = self.net.http_GET('{0}?{1}'.format(surl, urllib_parse.urlencode(data)), headers=headers).content
            sources = helpers.scrape_sources(shtml)
            if sources:
                headers.pop('X-Requested-With')
                return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
