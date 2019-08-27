# -*- coding: utf-8 -*-
# XStreamCDN resolver for ResolveURL
# Feb 22 2019
 
import json
 
from lib import helpers
from resolveurl.common import Net, RAND_UA
from resolveurl.resolver import ResolveUrl, ResolverError
 
 
class XStreamCDNResolver(ResolveUrl):
    name = 'XStreamCDN'
    domains = ["xstreamcdn.com", "gcloud.live", "there.to", "animeproxy.info", "myvidis.top"]
    pattern = '(?://|\.)((?:xstreamcdn\.com|gcloud\.live|there\.to|animeproxy\.info|myvidis\.top))/v/([\w-]+)'
 
    def __init__(self):
        self.net = Net()
        self.desktopHeaders = {
            'User-Agent': RAND_UA,
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'DNT': '1'
        }
 
 
    def get_media_url(self, host, media_id):
        self.desktopHeaders['Referer'] = self.get_url(host, media_id)
 
        r = self.net.http_POST(
            url = 'https://' + host + '/api/source/' + media_id,
            form_data = {'r': '', 'd': 'xstreamcdn.com'},
            headers = self.desktopHeaders
        )
        self.desktopHeaders['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.desktopHeaders['Cookie'] = '; '.join(cookie.name+'='+cookie.value for cookie in self.net._cj)
        del self.desktopHeaders['X-Requested-With']
        del self.desktopHeaders['Referer']
 
        jsonData = json.loads(r.content)
        if jsonData:
            source = helpers.pick_source(
                [(source.get('label', 'mp4'), source['file']) for source in jsonData['data']]
            )
            return source + helpers.append_headers(self.desktopHeaders)
        raise ResolverError('Unable to locate video')
 
 
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/v/{media_id}')

