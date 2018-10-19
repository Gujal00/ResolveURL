"""
    Kodi resolveurl plugin
    Copyright (C) 2014  smokdpi

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
import urllib
import urllib2
from lib import jsunpack
from urlparse import urlparse
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.hmf import HostedMediaFile

class VideoZooResolver(ResolveUrl):
    name = "videozoo"
    domains = ["byzoo.org", "playpanda.net", "videozoo.me", "videowing.me", "easyvideo.me", "play44.net", "playbb.me", "video44.net"]
    pattern = 'http://((?:www\.)*(?:play44|playbb|video44|byzoo|playpanda|videozoo|videowing|easyvideo)\.(?:me|org|net|eu)/(?:embed[/0-9a-zA-Z]*?|gplus|picasa|gogo/)(?:\.php)*)\?.*?((?:vid|video|id|file)=[%0-9a-zA-Z_\-\./]+|.*)[\?&]*.*'

    def __init__(self):
        self.net = common.Net()

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}?vid={media_id}')

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.IOS_USER_AGENT,
            'Referer': web_url
        }
        stream_url = ''
        new_host = urlparse(web_url).netloc
        html = self.net.http_GET(web_url, headers=headers).content
        if 'videozoo' not in new_host:
            r = re.search('(?:playlist:|timer\s*=\s*null;).+?url\s*[:=]+\s*[\'"]+(.+?)[\'"]+', html, re.DOTALL)
        else:
            r = re.search('\*/\s+?(eval\(function\(p,a,c,k,e,d\).+)\s+?/\*', html)
            if r:
                try:
                    r = jsunpack.unpack(r.group(1))
                    if r:
                        r = re.search('\[{"url":"(.+?)"', r.replace('\\', ''))
                except:
                    if r:
                        re_src = re.search('urlResolvers\|2F(.+?)\|', r.group(1))
                        re_url = re.search('php\|3D(.+?)\|', r.group(1))
                        if re_src and re_url:
                            stream_url = 'http://%s/%s.php?url=%s' % (new_host, re_src.group(1), re_url.group(1))
                            stream_url = self._redirect_test(stream_url)
                        else:
                            raise ResolverError('File not found')
        if r:
            stream_url = urllib.unquote_plus(r.group(1))
            if 'http' not in stream_url:
                stream_url = 'http://' + host + '/' + stream_url.replace('/gplus.php', 'gplus.php').replace('/picasa.php', 'picasa.php')
            stream_url = self._redirect_test(stream_url)

        if stream_url:
            if 'google' in stream_url:
                return HostedMediaFile(url=stream_url).resolve()
            else:
                return stream_url
        else:
            raise ResolverError('File not found')

    def _redirect_test(self, url):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', common.IOS_USER_AGENT)]
        opener.addheaders = [('Referer', urlparse(url).netloc)]
        try:
            resp = opener.open(url)
            if url != resp.geturl():
                return resp.geturl()
            else:
                return url
        except urllib2.HTTPError, e:
            if e.code == 403:
                if url != e.geturl():
                    return e.geturl()
            raise ResolverError('File not found')
