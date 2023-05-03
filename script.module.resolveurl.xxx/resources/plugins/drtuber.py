"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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
from six.moves import urllib_parse
import hashlib
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class DRTuberResolver(ResolveUrl):
    name = 'drtuber'
    domains = ['drtuber.com']
    pattern = r'(?://|\.)(drtuber\.com)/(?:embed|video)/(\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        params = "".join([x.replace("' + '", "") for x in self.between(html, "params += '", "';")])
        vkey = params.split('=')[-1]
        m = hashlib.md5()
        m.update((vkey + 'PT6l13umqV8K827').encode('utf-8'))
        params += '&pkey={0}'.format(m.hexdigest())
        params = urllib_parse.unquote(params)
        url = 'https://www.{0}/player_config/?{1}'.format(host, params)
        sources_html = self.net.http_GET(url, headers=headers).content
        if sources_html:
            srcs = re.findall(r'<((?:hq_)?video_file)>\<\!\[CDATA\[([^\]]+)', sources_html)
            if srcs:
                sources = []
                for k, v in srcs:
                    qual = {'video_file': '360p', 'hq_video_file': '720p'}.get(k)
                    sources.append((qual, v))
                return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/embed/{media_id}')

    def between(self, source, start, finish):
        """
            Helper method. Useful when parsing responses from web servers.

            Looks through a given source string for all items between two other strings,
            returns the list of items (or empty list if none are found).

            Example:
                test = 'hello >30< test >20< asdf >>10<< sadf>'
                print between(test, '>', '<')

            would print the list:
                ['30', '20', '>10']
        """
        result = []
        i = source.find(start)
        j = source.find(finish, i + len(start))

        while i >= 0 and j >= 0:
            i = i + len(start)
            result.append(source[i:j])
            i = source.find(start, j + len(finish))
            j = source.find(finish, i + len(start))

        return result

    @classmethod
    def _is_enabled(cls):
        return True
