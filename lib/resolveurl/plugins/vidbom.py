# -*- coding: utf-8 -*-
"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    ResolveUrl site plugin
    Copyright (C) 2018 gujal

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
from lib import helpers, aadecode
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VidBomResolver(ResolveUrl):
    name = "vidbom"
    domains = ['vidbom.com']
    pattern = '(?://|\.)(vidbom\.com)/(?:embed[/-])?([A-Za-z0-9]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            file_id = re.search("file_id',\s*'([^']+)",html)
            if file_id:
                headers.update({'cookie': 'lang=1; file_id={}'.format(file_id.group(1))})
                html = self.net.http_GET(web_url, headers=headers).content
            else:
                html = None
        
        if html:
            html = html.encode('utf-8')
            aa_text = re.search("""(ﾟωﾟﾉ\s*=\s*/｀ｍ´\s*）\s*ﾉ.+?;)\svar""", html, re.I)
            if aa_text:
                try:
                    aa_decoded = str(aadecode.decode(aa_text.group(1)))
                except:
                    raise ResolverError('Error decoding')
                
                sources = helpers.scrape_sources(aa_decoded)
                if sources:
                    headers.update({'Referer': web_url})
                    return helpers.pick_source(sources) + helpers.append_headers(headers)
        
        raise ResolverError('Video not found')
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
