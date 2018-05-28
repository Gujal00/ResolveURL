"""
    resolveurl XBMC Addon
    Copyright (C) 2015 tknorris

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
from resolveurl.resolver import ResolveUrl, ResolverError  # @UnusedImport
from lib import helpers

class FilePupResolver(ResolveUrl):
    name = "filepup"
    domains = ["filepup.net"]
    pattern = '(?://|\.)(filepup.(?:net))/(?:play|files)/([0-9a-zA-Z]+)'
    headers = {'User-Agent': common.RAND_UA}

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=self.headers).content
        default_url = self.__get_def_source(html)
        if default_url:
            qualities = self.__get_qualities(html)
            def_quality = self.__get_default(html)
            sources = []
            for quality in qualities:
                if quality == def_quality:
                    sources.append((quality, default_url))
                else:
                    stream_url = default_url.replace('.mp4?', '-%s.mp4?' % (quality))
                    sources.append((quality, stream_url))
            try: sources.sort(key=lambda x: int(x[0][:-1]), reverse=True)
            except: pass
            return helpers.pick_source(sources)

    def __get_def_source(self, html):
        default_url = ''
        match = re.search('sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
        if match:
            match = re.search('src\s*:\s*"([^"]+)', match.group(1))
            if match:
                default_url = match.group(1) + helpers.append_headers(self.headers)
        return default_url

    def __get_default(self, html):
        match = re.search('defaultQuality\s*:\s*"([^"]+)', html)
        if match:
            return match.group(1)
        else:
            return ''

    def __get_qualities(self, html):
        qualities = []
        match = re.search('qualities\s*:\s*\[(.*?)\]', html)
        if match:
            qualities = re.findall('"([^"]+)"', match.group(1))
        return qualities

    def get_url(self, host, media_id):
        return 'http://www.filepup.net/play/%s' % (media_id)
