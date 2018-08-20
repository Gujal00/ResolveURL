"""
resolveurl XBMC Addon
Copyright (C) 2011 t0mm0

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
"""
import re
import urllib2
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class EcostreamResolver(ResolveUrl):
    name = "ecostream"
    domains = ["ecostream.tv"]
    pattern = '(?://|\.)(ecostream.tv)/(?:stream|embed)?/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        if re.search('>File not found!<', html):
            raise ResolverError('File Not Found or removed')

        web_url = 'http://www.ecostream.tv/js/ecoss.js'
        js = self.net.http_GET(web_url).content
        r = re.search("\$\.post\('([^']+)'[^;]+'#auth'\).html\(''\)", js)
        if not r:
            raise ResolverError('Posturl not found')

        post_url = r.group(1)
        r = re.search('data\("tpm",([^\)]+)\);', js)
        if not r:
            raise ResolverError('Postparameterparts not found')
        post_param_parts = r.group(1).split('+')
        found_parts = []
        for part in post_param_parts:
            pattern = "%s='([^']+)'" % part.strip()
            r = re.search(pattern, html)
            if not r:
                raise ResolverError('Formvaluepart not found')
            found_parts.append(r.group(1))
        tpm = ''.join(found_parts)
        
        # emulate click on button "Start Stream"
        headers = ({'Referer': web_url, 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': common.EDGE_USER_AGENT})
        web_url = 'http://www.ecostream.tv' + post_url
        html = self.net.http_POST(web_url, {'id': media_id, 'tpm': tpm}, headers=headers).content
        sPattern = '"url":"([^"]+)"'
        r = re.search(sPattern, html)
        if not r:
            raise ResolverError('Unable to resolve Ecostream link. Filelink not found.')
        stream_url = 'http://www.ecostream.tv' + r.group(1)
        stream_url = urllib2.unquote(stream_url)
        stream_url = urllib2.urlopen(urllib2.Request(stream_url, headers=headers)).geturl()

        return stream_url + helpers.append_headers({'User-Agent': common.EDGE_USER_AGENT})

    def get_url(self, host, media_id):
        return 'http://www.ecostream.tv/stream/%s.html' % (media_id)
