"""
    Kodi resolveurl plugin
    Copyright (C) 2017  script.module.resolveurl

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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VidicsResolver(ResolveUrl):
    name = 'vidics'
    domains = ['vidics.tv']
    pattern = '(?://|\.)(vidics\.tv)/embed/([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
        
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            quals = re.findall("""href=["'].+?id=["'](\d{3,4})p""", html)
            source = re.search("""mp4\d+\s*=\s*["']([^"']+)""", html)
            if source:
                headers.update({'Referer': web_url})
                if len(quals) > 1:
                    sources = [(qual, re.sub('-\d{3,4}\.', '-%s.' % qual, source.group(1))) for qual in quals]
                    try: sources.sort(key=lambda x: int(re.sub("\D", "", x[0])), reverse=True)
                    except: common.logger.log_debug('Scrape sources sort failed |int(re.sub("\D", "", x[0])|')
                    return helpers.pick_source(sources) + helpers.append_headers(headers)
                else:
                    return source.group(1) + helpers.append_headers(headers)
            
        raise ResolverError('Unable to locate video')
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://embed1.{host}/embed/{media_id}/')
