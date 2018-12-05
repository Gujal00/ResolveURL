'''
    resolveurl Kodi plugin
    Copyright (C) 2018

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
'''
import re
import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class FembedResolver(ResolveUrl):
    name = "fembed"
    domains = ["fembed.com"]
    pattern = '(?://|\.)(fembed\.com)/v/([a-zA-Z0-9]+)'

    def __init__(self):
        self.net = common.Net()
        
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.RAND_UA}
        api_url = 'https://www.%s/api/source/%s' % (host, media_id)
        js_result = self.net.http_POST(api_url, form_data={'r': ''}, headers=headers).content
        
        if js_result:
            try:
                js_data = json.loads(js_result)
                if js_data.get('success'):
                    sources = [(i.get('label'), 'https://www.%s%s' % (host, i.get('file'))) for i in js_data.get('data') if i.get('type') == 'mp4']
                    common.logger.log(sources)
                    if len(sources) > 1:
                        try: sources.sort(key=lambda x: int(re.sub("\D", "", x[0])), reverse=True)
                        except: 
                            common.logger.log_debug('Scrape sources sort failed |int(re.sub("\D", "", x[0])|')
                            try: sources.sort(key=lambda x: re.sub("[^a-zA-Z]", "", x[0]))
                            except: common.logger.log_debug('Scrape sources sort failed |re.sub("[^a-zA-Z]", "", x[0])|')
                    return helpers.pick_source(sources) + helpers.append_headers(headers)
                else:
                    raise Exception(js_data.get('data'))
            except Exception as e:
                raise ResolverError('Error getting video: %s' % e)
                
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.{host}/v/{media_id}')
