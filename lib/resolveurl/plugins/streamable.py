"""
    resolveurl XBMC Addon
    Copyright (C) 2017 tknorris

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
import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class StreamableResolver(ResolveUrl):
    name = "Streamable"
    domains = ['streamable.com']
    pattern = '(?://|\.)(streamable\.com)/(?:s/)?([a-zA-Z0-9]+(?:/[a-zA-Z0-9]+)?)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search('videoObject\s*=\s*(.*?});', html)
        if match:
            try: js_data = json.loads(match.group(1))
            except: js_data = {}
            streams = js_data.get('files', {})
            sources = [(stream.get('height', 'Unknown'), stream['url']) for _key, stream in streams.iteritems()]
            sources = [(label, 'https:' + stream_url) if stream_url.startswith('//') else (label, stream_url) for label, stream_url in sources]
            sources.sort(key=lambda x: x[0], reverse=True)
            return helpers.pick_source(sources) + helpers.append_headers(headers)
        else:
            raise ResolverError('JSON Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/s/{media_id}')
