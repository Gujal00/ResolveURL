"""
    Plugin for ResolveUrl
    Copyright (C) 2019 gujal

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

from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from six.moves import urllib_request, urllib_error


class StreamzResolver(ResolveUrl):
    name = "streamz"
    domains = ['streamz.cc', "streamz.vg"]
    pattern = r'(?://|\.)(streamz\.(?:cc|vg))/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):

        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        html += helpers.get_packed_data(html)
        sources = helpers.scrape_sources(html)

        if sources:
            headers.update({'Referer': web_url})
            return self._redirect_test(helpers.pick_source(sources)) + helpers.append_headers(headers)
        else:
            raise ResolverError("Video not found")

    def get_url(self, host, media_id):

        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    def _redirect_test(self, url):
        opener = urllib_request.build_opener()
        opener.addheaders = [('User-agent', common.CHROME_USER_AGENT)]
        try:
            resp = opener.open(url)
            if url != resp.geturl():
                return resp.geturl()
            else:
                return url
        except urllib_error.HTTPError as e:
            if e.code == 403:
                if url != e.geturl():
                    return e.geturl()
            raise ResolverError('File not found')
