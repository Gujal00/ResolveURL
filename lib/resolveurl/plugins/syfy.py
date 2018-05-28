'''
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
import re, datetime, json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class SyFyResolver(ResolveUrl):
    name = "SyFy"
    domains = ["syfy.com"]
    pattern = "(?://|\.)(syfy\.com)/(\w+/videos/[a-zA-Z0-9_\-']+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            try:
                purl = re.compile('data-src="(.+?)"', re.DOTALL).search(html)
                purl = purl.group(1)
                purl = 'http:' + purl.replace('&amp;', '&')
                html = self.net.http_GET(purl, headers=headers).content
                purl = re.compile('<link rel="alternate" href=".+?<link rel="alternate" href="(.+?)"', re.DOTALL).search(html).group(1)
                purl += '&format=Script&height=576&width=1024'
                html = self.net.http_GET(purl, headers=headers).content
                a = json.loads(html)
                url = a["captions"][0]["src"]
                url = url.split('/caption/',1)[1]
                url_snippit = url.split('.',1)[0]
                url_template = 'https://tvesyfy-vh.akamaihd.net/i/prod/video/%s_,25,40,18,12,7,4,2,00.mp4.csmil/master.m3u8?__b__=1000&hdnea=st=%s~exp=%s'
                curr_time = (datetime.datetime.utcnow()- datetime.datetime(1970,1,1))
                start_time = int((curr_time.microseconds + (curr_time.seconds + curr_time.days * 24 * 3600) * 10**6) / 10**6)
                resolved_url = url_template % (url_snippit, str(start_time), str(start_time+60))
                headers.update({'Referer': web_url})
                
                return resolved_url + helpers.append_headers(headers)
                
            except:
                raise ResolverError('Video not found')
                
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/{media_id}')
