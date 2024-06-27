"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal
    Copyright (C) 2024 MrDini123 (github.com/movieshark)

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

from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse
from resolveurl.lib import helpers


class LiiVideoResolver(ResolveUrl):
    name = 'LiiVideo'
    domains = ['liivideo.com', 'liiivideo.com', 'cimastream.xyz']
    pattern = r'(?://|\.)(liii?video\.com|cimastream\.xyz)/(?:d|e)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        data = {
            'op': 'embed',
            'file_code': media_id,
            'auto': 1,
            'referer': '' # intentionally blank
        }
        dl_url = urllib_parse.urljoin(web_url, '/dl')
        html = self.net.http_POST(dl_url, data, headers=headers).content
        sources = helpers.scrape_sources(
            html,
            result_blacklist=['.mpd'],
            patterns=[r'file:"(?P<url>[^"]+)'],
            generic_patterns=False
        )
        if sources:
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        # alternative method using download page
        html = self.net.http_GET(web_url, headers=headers).content
        form = helpers.get_hidden(html, 'F1')
        if form:
            html = self.net.http_POST(dl_url, form, headers=headers).content
            sources = helpers.scrape_sources(
                html,
                result_blacklist=['.mpd'],
                patterns=[r'href="(?P<url>https://[^"]+)"[^>]+>Direct Download Link'],
                generic_patterns=False
            )
            if sources:
                return helpers.pick_source(sources) + helpers.append_headers(headers)
        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/d/{media_id}_n')
