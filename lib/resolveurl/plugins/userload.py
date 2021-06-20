"""
Plugin for ResolveUrl
Copyright (C) 2021 gujal

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
from resolveurl.plugins.lib import helpers, jsunhunt
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class UserLoadResolver(ResolveUrl):
    name = "UserLoad"
    domains = ['userload.co']
    pattern = r'(?://|\.)(userload\.co)/(?:e|f|embed)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        blurl = 'https://{0}/api/assets/userload/js/form.framework.js'.format(host)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        html = helpers.get_packed_data(html)
        headers.update({'Referer': web_url})
        bl = self.net.http_GET(blurl, headers=headers).content
        if jsunhunt.detect(bl):
            bl = jsunhunt.unhunt(bl)
        b1 = re.search(r'url:\s*"([^"]+)', bl)
        b2 = re.search(r'data:\s*{([^}]+)', bl)
        if b1 and b2:
            bd = re.findall(r'"([^"]+)":\s*([^,\s]+)', b2.group(1))
            data = {}
            for key, var in bd:
                r = re.search(r'{0}\s*=\s*"([^"]+)'.format(var), html)
                if r:
                    data.update({key: r.group(1)})

            if data:
                api_url = 'https://{0}{1}'.format(host, b1.group(1))
                headers.update({
                    'X-Requested-With': 'XMLHttpRequest',
                    'Origin': 'https://{0}'.format(host)
                })
                stream_url = self.net.http_POST(api_url, data, headers=headers).content
                headers.pop('X-Requested-With')
                stream_url = helpers.get_redirect_url(stream_url, headers)
                return stream_url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
