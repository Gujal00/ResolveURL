"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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

import binascii
import json
import re
from six.moves import urllib_parse, urllib_error
from resolveurl import common
from resolveurl.lib import helpers, aadecode
from resolveurl.resolver import ResolveUrl, ResolverError


class VidGuardResolver(ResolveUrl):
    name = 'VidGuard'
    domains = ['vidguard.to', 'vgfplay.com', 'vgembed.com', 'moflix-stream.day',
               'v6embed.xyz', 'vid-guard.com', 'vembed.net', 'embedv.net', 'fslinks.org',
               'bembed.net', 'listeamed.net', 'gsfjzmqu.sbs']
    pattern = r'(?://|\.)((?:vid-?guard|vgfplay|fslinks|moflix-stream|listeamed|gsfjzmqu|v?[g6b]?embedv?)' \
              r'\.(?:to|com|day|xyz|org|net|sbs))/(?:e|v|d)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        try:
            html = self.net.http_GET(web_url, headers=headers).content
        except urllib_error.HTTPError:
            raise ResolverError('The requested video was not found.')

        r = re.search(r'eval\("window\.ADBLOCKER\s*=\s*false;\\n(.+?);"\);</script', html)
        if r:
            r = r.group(1).replace('\\u002b', '+')
            r = r.replace('\\u0027', "'")
            r = r.replace('\\u0022', '"')
            r = r.replace('\\/', '/')
            r = r.replace('\\\\', '\\')
            r = r.replace('\\"', '"')
            aa_decoded = aadecode.decode(r, alt=True)
            stream_url = json.loads(aa_decoded[11:]).get('stream')
            if stream_url:
                if isinstance(stream_url, list):
                    sources = [(x.get('Label'), x.get('URL')) for x in stream_url]
                    stream_url = helpers.pick_source(helpers.sort_sources_list(sources))
                if not stream_url.startswith('https://'):
                    stream_url = re.sub(':/*', '://', stream_url)
                headers.update({'Referer': urllib_parse.urljoin(web_url, '/')})
                return self.sig_decode(stream_url) + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        hosts = ['vidguard', 'vid-guard', 'vgfplay', 'vgembed', 'vembed.net', 'embedv.net']
        if any(x in host for x in hosts):
            host = 'listeamed.net'
        return self._default_get_url(host, media_id, 'https://{host}/e/{media_id}')

    # Adapted from PHP code by vb6rocod
    # Copyright (c) 2019 vb6rocod
    def sig_decode(self, url):
        sig = url.split('sig=')[1].split('&')[0]
        t = ''
        for v in binascii.unhexlify(sig):
            t += chr((v if isinstance(v, int) else ord(v)) ^ 2)
        t = list(helpers.b64decode(t + '==')[:-5][::-1])
        for i in range(0, len(t) - 1, 2):
            t[i + 1], t[i] = t[i], t[i + 1]
        url = url.replace(sig, ''.join(t)[:-5])
        return url
