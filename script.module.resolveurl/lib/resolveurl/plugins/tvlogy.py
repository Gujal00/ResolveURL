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
import random
import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class TVLogyResolver(ResolveUrl):
    name = 'TVLogy'
    domains = ['tvlogy.to']
    pattern = r'(?://|\.)((?:hls\.|flow\.)?tvlogy\.to)/(?:embed/|watch\.php\?v=|player/index.php\?data=)?([0-9a-zA-Z/]+)'

    def get_media_url(self, host, media_id):
        embeds = ['http://bestarticles.me/', 'http://tellygossips.net/', 'http://tvarticles.org/']
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}

        if 'hls.' in web_url:
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            pdata = {'hash': media_id,
                     'r': 'https://{0}/'.format(host)}
            resp = json.loads(self.net.http_POST(web_url, form_data=pdata, headers=headers).content)
            str_url = resp.get('videoSource')
            if str_url:
                headers.pop('X-Requested-With')
                return str_url + helpers.append_headers(headers)
        else:
            headers.update({'Referer': random.choice(embeds)})
            html = self.net.http_GET(web_url, headers=headers).content

            if 'Not Found' in html:
                raise ResolverError('File Removed')

            if 'Video is processing' in html:
                raise ResolverError('File still being processed')

            html += helpers.get_packed_data(html)
            packed = re.search(r"JuicyCodes\.Run\((.+?)\)", html, re.I)
            if packed:
                from base64 import b64decode
                packed = packed.group(1).replace('"', '').replace('+', '')
                packed = b64decode(packed.encode('ascii'))
                html += '%s</script>' % packed.decode('latin-1').strip()

            source = helpers.scrape_sources(html, patterns=[r'''"file":\s*"(?P<url>[^"]+\.(?:m3u8|mp4|txt))"'''])
            if source:
                headers.update({'Referer': web_url, 'Accept': '*/*'})
                vsrv = re.search(r'//(\d+)/', source[0][1])
                if vsrv:
                    source = re.sub(r"//\d+/", "//{0}/".format(host), source[0][1]) + '?s={0}&d='.format(vsrv.group(1))
                    disk = re.findall(r'videoDisk":\s*"([^"]+)', html)
                    if disk:
                        disk = helpers.b64encode(disk[0])
                        source += disk
                else:
                    source = source[0][1]
                html = self.net.http_GET(source, headers=headers).content
                sources = re.findall(r'RESOLUTION=\d+x(\d+)\n([^\n]+)', html)
                src = helpers.pick_source(helpers.sort_sources_list(sources))
                if not src.startswith('http'):
                    src = re.sub(source.split('/')[-1], src, source)
                return src + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        if 'hls.' in host:
            template = 'https://{host}/player/index.php?data={media_id}&do=getVideo'
        else:
            template = 'https://{host}/{media_id}'
        return self._default_get_url(host, media_id, template=template)
