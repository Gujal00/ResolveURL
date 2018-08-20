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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import re
import random

class RapidVideoResolver(ResolveUrl):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com"]
    pattern = '(?://|\.)(rapidvideo\.com)/(?:[ev]/|embed/|\?v=)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        web_url = web_url.replace('/embed/','/e/')
        headers['Referer'] = 'https://www.rapidvideo.com/'
        formdata = {'confirm.x':random.randint(50,80),
                    'confirm.y':random.randint(50,80),
                    'block':1}
        html =  self.net.http_POST(web_url, form_data=formdata, headers=headers).content
        r = re.search('href="([^&"]+&q=[^"]+)">\n.+?>\s*([^<\n]+)',html)
        if r:
            sources = []
            srcs = re.findall('href="([^&"]+&q=[^"]+)">\n.+?>\s*([^<\n]+)',html)
            for src,qual in srcs:
                shtml = self.net.http_POST(src, form_data=formdata, headers=headers).content
                strurl = re.findall('source\s*src="([^"]+)',shtml)[0]
                sources.append((qual,strurl))
            
            return helpers.pick_source(sources) + helpers.append_headers({'User-Agent': common.FF_USER_AGENT})
        else:
            raise ResolverError('File Not Found or removed')
        
        return strurl

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
