"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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

import re, string, struct, base64, random
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from six.moves import urllib_parse
import six


class VideaResolver(ResolveUrl):
    name = 'Videa'
    domains = ['videa.hu', 'videakid.hu']
    pattern = r'(?://|\.)((?:videa|videakid)\.hu)/(?:player/?\?v=|player/v/|videok/)(?:.*-|)([0-9a-zA-Z]+)'
    url = ''
    videa_secret = 'xHb0ZvME5q8CBcoQi6AngerDu3FGO9fkUlwPmLVY_RTzj2hJIS4NasXWKy1td7p'
    key = ''

    def rc4(self, cipher_text, key):
        def compat_ord(c):
            return c if isinstance(c, int) else ord(c)

        res = b''

        key_len = len(key)
        S = list(range(256))

        j = 0
        for i in range(256):
            j = (j + S[i] + ord(key[i % key_len])) % 256
            S[i], S[j] = S[j], S[i]

        i = 0
        j = 0
        for m in range(len(cipher_text)):
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            k = S[(S[i] + S[j]) % 256]
            res += struct.pack('B', k ^ compat_ord(cipher_text[m]))

        if six.PY3:
            return res.decode()
        else:
            return res

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        result = self.net.http_GET(web_url)

        videaXml = result.content
        if not videaXml.startswith('<?xml'):
            self.key += result.get_headers(as_dict=True)['X-Videa-Xs']
            videaXml = self.rc4(base64.b64decode(videaXml), self.key)
        sources = re.findall(r'video_source\s*name="(?P<label>[^"]+).*exp="(?P<exp>[^"]+)[^>]+>(?P<url>[^<]+)', videaXml)

        if sources:
            tmpSources = []
            for index, source in enumerate(sources):
                tmpSources.append((source[0], index))
            source = sources[helpers.pick_source(helpers.sort_sources_list(tmpSources))]
            url = 'https:' + source[2] if source[2].startswith('//') else source[2]
            hash = re.search(r'<hash_value_%s>([^<]+)<' % source[0], videaXml).group(1)
            direct_url = "%s?md5=%s&expires=%s" % (url, hash, source[1])
            return direct_url.replace('&amp;', '&')

        raise ResolverError('Stream not found')

    def get_url(self, host, media_id):
        html = self.net.http_GET(self.url).content
        if '%s/player' % host in self.url:
            player_url = self.url
            player_page = html
        else:
            player_url = re.search(r'<iframe.*?src="(/player\?[^"]+)"', html).group(1)
            player_url = urllib_parse.urljoin(self.url, player_url)
            player_page = self.net.http_GET(player_url).content
        nonce = re.search(r'_xt\s*=\s*"([^"]+)"', player_page).group(1)
        l = nonce[:32]
        s = nonce[32:]
        result = ''
        for i in range(0, 32):
            result += s[i - (self.videa_secret.index(l[i]) - 31)]
        query = urllib_parse.parse_qs(urllib_parse.urlparse(player_url).query)
        random_seed = ''
        for i in range(8):
            random_seed += random.choice(string.ascii_letters + string.digits)
        _s = random_seed
        _t = result[:16]
        self.key = result[16:] + random_seed
        if 'f' in query or 'v' in query:
            _param = 'f=%s' % query['f'][0] if 'f' in query else 'v=%s' % query['v'][0]
            return self._default_get_url(host, media_id, 'https://{host}/player/xml?platform=desktop&%s&_s=%s&_t=%s' % (_param, _s, _t))
        else:
            return None

    def get_host_and_id(self, url):
        self.url = url
        return super(VideaResolver, self).get_host_and_id(url)