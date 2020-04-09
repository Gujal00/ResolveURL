"""
    plugin for ResolveURL
    Copyright (C) 2020 gujal

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
import urllib
import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class CdaResolver(ResolveUrl):
    name = "cda"
    domains = ['m.cda.pl', 'cda.pl', 'www.cda.pl', 'ebd.cda.pl']
    pattern = r'(?://|\.)(cda\.pl)/(?:.\d+x\d+|video)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.RAND_UA}

        html = self.net.http_GET(web_url, headers=headers).content
        sources = re.findall('data-quality.+?href="(?P<url>[^"]+).+?>(?P<label>[^<]+)', html)
        if sources:
            sources = [(source[1], source[0]) for source in sources]
            html = self.net.http_GET(helpers.pick_source(helpers.sort_sources_list(sources)), headers=headers).content
            match = re.search(r"player_data='([^']+)", html)
            if match:
                js_data = json.loads(match.group(1))
                return self.cda_decode(js_data.get('video').get('file')) + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://ebd.cda.pl/647x500/{media_id}/vfilm')

    def cda_decode(self, url):
        url = urllib.unquote(url)
        a = ''.join([chr(33 + (ord(char) + 14) % 94) if 32 < ord(char) < 127 else char for char in url])
        a = a[:-4].replace(".cda.mp4", "")
        a = a.replace(".2cda.pl", ".cda.pl")
        a = a.replace(".3cda.pl", ".cda.pl")
        return "https://{0}.mp4".format(a)
