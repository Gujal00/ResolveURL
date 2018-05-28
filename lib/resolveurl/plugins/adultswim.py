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
import re, json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class AdultSwimResolver(ResolveUrl):
    name = "AdultSwim"
    domains = ["adultswim.com"]
    pattern = "(?://|\.)(adultswim\.com)/videos/((?!streams)[a-z\-]+/[a-z\-]+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            try:
                json_data = re.search("""__AS_INITIAL_DATA__\s*=\s*({.*?});""", html).groups()[0]
                json_data = json_data.replace("\/", "/")
                a = json.loads(json_data)
                ep_id = a["show"]["sluggedVideo"]["id"]
                api_url = 'http://www.adultswim.com/videos/api/v0/assets?platform=desktop&id=%s&phds=true' % ep_id
                
                return helpers.get_media_url(api_url, patterns=["""<file .*?type="(?P<label>[^"]+).+?>(?P<url>[^<\s]+)"""], result_blacklist=[".f4m"]).replace(' ', '%20')
                
            except Exception as e:
                raise ResolverError(e)
                
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/videos/{media_id}')
