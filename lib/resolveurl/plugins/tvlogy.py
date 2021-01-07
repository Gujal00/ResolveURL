"""
    Plugin for ResolveUrl
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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class TVLogyResolver(ResolveUrl):
    name = "tvlogy.to"
    domains = ["tvlogy.to"]
    pattern = r'(?://|\.)((?:hls\.)?tvlogy\.to)/(?:embed/|watch\.php\?v=|player/index.php\?data=)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if 'Not Found' in html:
            raise ResolverError('File Removed')

        if 'Video is processing' in html:
            raise ResolverError('File still being processed')

        packed = re.search(r"JuicyCodes\.Run\((.+?)\)", html, re.I)
        if packed:
            from base64 import b64decode
            packed = packed.group(1).replace('"', '').replace('+', '')
            packed = b64decode(packed.encode('ascii'))
            html += '%s</script>' % packed.decode('latin-1').strip()

        source = helpers.scrape_sources(html)
        if source:
            headers.update({'Referer': web_url, 'Accept': '*/*'})
            vsrv = re.findall(r'//(\d+)/', source[0][1])[0]
            source = re.sub(r"//\d+/", "//{0}/".format(host), source[0][1]) + '?s={0}&d='.format(vsrv)
            html = self.net.http_GET(source, headers=headers).content
            sources = re.findall(r'RESOLUTION=\d+x(\d+)\n([^\n]+)', html)
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}')
