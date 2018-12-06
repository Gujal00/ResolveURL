# -*- coding: utf-8 -*-
"""
resolveurl Kodi Plugin
Copyright (C) 2018 Gujal

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
import urllib2
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class RapidVideoResolver(ResolveUrl):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com"]
    pattern = '(?://|\.)(rapidvideo\.com)/(?:[ev]/|embed/|\?v=|embed/\?v=)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        
        try:
            html = self.net.http_GET(web_url, headers=headers).content
        except  urllib2.HTTPError as e:
            if e.code == 404:
                raise ResolverError("Video not found")

        srcs = re.findall(r'href="(%s&q=[^"]+)' % web_url, html, re.I)
        if srcs:
            sources = []
            for src in srcs:
                shtml = self.net.http_GET(src, headers=headers).content
                strurl = helpers.parse_html5_source_list(shtml)
                if strurl:
                    sources.append(strurl[0])
            sources = helpers.sort_sources_list(sources)
        else:
            sources = helpers.parse_html5_source_list(html)
        
        if len(sources) > 0:
            return helpers.pick_source(sources) + helpers.append_headers(headers)
        else:
            raise ResolverError("Video not found")
            

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/e/{media_id}')
