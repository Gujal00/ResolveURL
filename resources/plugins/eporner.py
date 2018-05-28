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
import re, json
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError

class EpornerResolver(ResolveUrl):
    name = 'eporner'
    domains = ['eporner.com']
    pattern = '(?://|\.)(eporner\.com)/[\w\-]+/([a-zA-Z0-9]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            try:
                pattern = r"""{\s*vid:\s*'([^']+)',\s*hash\s*:\s*["\']([\da-f]{32})"""
                id, hash = re.findall(pattern, html)[0]
                hash_code = ''.join((self.encode_base_n(int(hash[lb:lb + 8], 16), 36) for lb in range(0, 32, 8)))
                load_url = 'https://www.eporner.com/xhr/video/%s?hash=%s&device=generic&domain=www.eporner.com&fallback=false&embed=false&supportedFormats=mp4' % (id, hash_code)
                headers.update({'Referer': web_url})
                r = self.net.http_GET(load_url, headers=headers).content
                r = r.replace("\/", "/")
                r = json.loads(r).get("sources", {}).get('mp4', {})
                sources = [(i, r[i].get("src")) for i in r]
                if len(sources) > 1:
                    try: sources.sort(key=lambda x: int(re.sub("\D", "", x[0])), reverse=True)
                    except: common.logger.log_debug('Scrape sources sort failed |int(re.sub("\D", "", x[0])|')
                
                return helpers.pick_source(sources) + helpers.append_headers(headers)
                
            except: 
                raise ResolverError('File not found')
        
        raise ResolverError('File not found')
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/embed/{media_id}')

    # needed to generate hash for eporner
    def encode_base_n(self, num, n, table=None):
        FULL_TABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if not table:
            table = FULL_TABLE[:n]
        
        if n > len(table):
            raise ValueError('base %d exceeds table length %d' % (n, len(table)))
        
        if num == 0:
            return table[0]
        
        ret = ''
        while num:
            ret = table[num % n] + ret
            num = num // n
        return ret

    @classmethod
    def _is_enabled(cls):
        return True
