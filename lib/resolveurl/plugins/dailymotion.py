'''
dailymotion resolveurl plugin
Copyright (C) 2011 cyrus007

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
import json
import re
import urllib
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class DailymotionResolver(ResolveUrl):
    name = 'dailymotion'
    domains = ['dailymotion.com']
    pattern = '(?://|\.)(dailymotion\.com)/(?:video|embed|sequence|swf)(?:/video)?/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.RAND_UA}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=self.headers).content
        """if '"reason":"video attribute|explicit"' in html:
            headers = {'Referer': web_url}
            headers.update(self.headers)
            url_back = '/embed/video/%s' % (media_id)
            web_url = 'http://www.dailymotion.com/family_filter?enable=false&urlback=%s' % (urllib.quote_plus(url_back))
            html = self.net.http_GET(url=web_url, headers=headers).content"""
        
        if '"title":"Content rejected."' in html: raise ResolverError('This video has been removed due to a copyright claim.')
        
        match = re.search('var\s+config\s*=\s*(.*?}});', html)
        if not match: raise ResolverError('Unable to locate config')
        try: js_data = json.loads(match.group(1))
        except: js_data = {}
        
        sources = []
        streams = js_data.get('metadata', {}).get('qualities', {})
        for quality, links in streams.iteritems():
            for link in links:
                if quality.isdigit() and link.get('type', '').startswith('video'):
                    sources.append((quality, link['url']))
                
        sources.sort(key=lambda x: self.__key(x), reverse=True)
        return helpers.pick_source(sources) + helpers.append_headers(self.headers)
    
    def __key(self, item):
        try: return int(item[0])
        except: return 0

    def get_url(self, host, media_id):
        return 'http://www.dailymotion.com/embed/video/%s' % media_id
