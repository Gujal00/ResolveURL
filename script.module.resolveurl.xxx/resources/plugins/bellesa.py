"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class BellesaResolver(ResolveUrl):
    name = 'Bellesa'
    domains = ['bellesa.co']
    pattern = r'(?://|\.)(bellesa\.co)/videos/([0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://www.{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content

        r = re.search(r'"id":\s*{0}.+?"source":\s*"([^"]+).+?"resolutions":\s*"([^"]+)'.format(media_id), html)
        if r:
            vid = r.group(1)
            quals = r.group(2).split(',')
            sources = [(qual, 'https://s.bellesa.co/v/{0}/{1}.mp4'.format(vid, qual)) for qual in quals]
            url = helpers.pick_source(helpers.sort_sources_list(sources))
            return url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/videos/{media_id}/')

    @classmethod
    def _is_enabled(cls):
        return True
