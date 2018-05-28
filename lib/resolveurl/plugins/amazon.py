"""
    Kodi resolveurl plugin
    Copyright (C) 2016  script.module.resolveurl

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
import time, json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class AmazonCloudResolver(ResolveUrl):
    name = 'amazon_clouddrive'
    domains = ['amazon.com']
    pattern = '(?://|\.)(amazon\.com)/clouddrive/share/([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
        
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': 'https://www.amazon.com/'}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            try:
                node_info = json.loads(html)
                node_id = node_info["nodeInfo"]["id"]
                node_url = 'https://www.amazon.com/drive/v1/nodes/%s/children?asset=ALL&tempLink=true&limit=1&searchOnFamily=false&shareId=%s&offset=0&resourceVersion=V2&ContentType=JSON&_=%s323' % (node_id, media_id, time.time())
                html = None
                html = self.net.http_GET(node_url, headers=headers).content
                if html:
                    source_info = json.loads(html)
                    source = source_info["data"][0]["tempLink"]
                    
                    if source:
                        source = "%s?download=true" % source
                        return source + helpers.append_headers(headers)
            except:
                raise ResolverError('Unable to locate video')
            
        raise ResolverError('Unable to locate video')
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/drive/v1/shares/{media_id}?shareId={media_id}&resourceVersion=V2&ContentType=JSON&_=%s322' % time.time())
