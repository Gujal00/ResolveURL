"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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
from resolveurl.lib import helpers, jsunhunt
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class UpVideoResolver(ResolveUrl):
    name = 'UpVideo'
    domains = ['upvideo.to', 'videoloca.xyz', 'tnaket.xyz', 'makaveli.xyz',
               'highload.to', 'embedo.co']
    pattern = r'(?://|\.)((?:upvideo|videoloca|makaveli|tnaket|highload|embedo)\.' \
              r'(?:to|xyz|co))/(?:e|v|f)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        headers.update({'Referer': web_url})

        if 'sorry' in html:
            raise ResolverError("Video Deleted")

        if jsunhunt.detect(html):
            html = re.findall('<head>(.+?)</head>', html, re.DOTALL)[0]
            html = jsunhunt.unhunt(html)

        aurl = 'https://{0}/assets/js/tabber.js'.format(host)
        ahtml = self.net.http_GET(aurl, headers=headers).content
        if not jsunhunt.detect(ahtml):
            aurl = 'https://{0}/assets/js/master.js'.format(host)
            ahtml = self.net.http_GET(aurl, headers=headers).content

        if jsunhunt.detect(ahtml):
            ahtml = jsunhunt.unhunt(ahtml)
            var, rep1, rep2 = re.findall(
                r'''var\s*res\s*=\s*([^.]+)\.replace\("([^"]+).+?replace\("([^"]+)''',
                ahtml, re.DOTALL)[0]
            r = re.search(r'var\s*{0}\s*=\s*"([^"]+)'.format(var), html)
            if r:
                surl = r.group(1).replace(rep1, '')
                surl = surl.replace(rep2, '')
                surl = helpers.b64decode(surl)
                if host.split('.')[0] in ['embedo', 'highload']:
                    headers.update({'verifypeer': 'false'})
                return surl.replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError("Video not found")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
