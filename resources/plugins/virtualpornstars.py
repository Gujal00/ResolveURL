'''
    resolveurl XBMC Addon
    Copyright (C) 2016 Gujal

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
'''
import re, sys, urllib2, ssl
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError

class VirtualPornStarsResolver(ResolveUrl):
    name = 'virtualpornstars'
    domains = ['virtualpornstars.com']
    pattern = '(?://|\.)(virtualpornstars\.com)/(?:\w+/)?([\w\-]+)'
    
    def __init__(self):
        if sys.version_info < (2, 7, 9): raise ResolverError('Python 2.7.9 or greater required')
        self.context = ssl._create_unverified_context()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        request = urllib2.Request(web_url, headers=headers) 
        response = urllib2.urlopen(request, context=self.context)
        html = response.read()
        
        if html:
            try:
                headers.update({'Referer': web_url})
                source = re.search('''file:\s*["']([^"']+)''', html).groups()[0]
                
                return source + helpers.append_headers(headers)
                
            except:
                raise ResolverError('File not found')
                
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
        
    @classmethod
    def _is_enabled(cls):
        return False if sys.version_info < (2, 7, 9) else True
