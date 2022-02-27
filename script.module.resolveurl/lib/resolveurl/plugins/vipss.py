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
import re
import json
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VipSSResolver(ResolveUrl):
    name = "vipss"
    domains = ['vipss.club']
    pattern = r'(?://|\.)(vipss\.club)/([a-zA-Z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content

        file_id = re.search(r'showFileInformation\((\d+)', html)
        if file_id:
            aurl = 'https://{0}/ajax/_account_file_details.ajax.php'.format(host)
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            form_data = {'u': file_id.group(1)}
            spage = self.net.http_POST(aurl, form_data=form_data, headers=headers).content
            spage = json.loads(spage).get('html')
            srcs = helpers.scrape_sources(spage, patterns=[r'''file:\s*"(?P<url>[^"']+)'''])
            if srcs:
                headers.pop('X-Requested-With')
                return helpers.pick_source(srcs) + helpers.append_headers(headers)

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}/')
