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

from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class VidMojoResolver(ResolveUrl):
    name = 'VidMojo'
    domains = ['vidmojo.net', 'vidflare.net', 'embedojo.com']
    pattern = r'(?://|\.)((?:vid(?:mojo|flare)|embedojo)\.(?:net|com))/(?:embed-)?([^\n]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False

        web_url = self.get_url(host, media_id)
        if not referer:
            referer = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        response = self.net.http_GET(web_url, headers=headers).content
        srcs = helpers.scrape_sources(response, patterns=[r'''sources:\s*[[{]+\s*file:\s*"(?P<url>[^"]+)'''], generic_patterns=False)
        if srcs:
            headers.update({
                'Referer': 'https://{0}/'.format(host),
                'Origin': 'https://{0}'.format(host)
            })
            return helpers.pick_source(sorted(srcs, reverse=True)) + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}')
