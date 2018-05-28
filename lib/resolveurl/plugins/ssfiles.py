"""
    resolveurl plugin
    Copyright (C) 2018 Gujal
    
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

class SsfilesResolver(ResolveUrl):
    name = 'ssfiles.com'
    domains = ['ssfiles.com']
    pattern = '(?://|\.)(ssfiles\.com)/(?:embed-)?([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        _html = self.net.http_GET(web_url, headers=headers).content

        if _html:
            if 'Not Found' in _html:
                msg = 'File Removed'
                raise ResolverError(msg)
                
            _sources = re.search('''sources\s*:\s*\[(.+?)\]''', _html)
            if _sources:
                sources = helpers.scrape_sources(_sources.group(1), result_blacklist=[".smil"], patterns=['''["'](?P<url>[^"',\s]+)'''], generic_patterns=False)
                if sources:
                    headers.update({'Referer': web_url})
                    return helpers.pick_source(sources) + helpers.append_headers(headers)
                
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
