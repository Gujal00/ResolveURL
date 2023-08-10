"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de

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
from resolveurl import common
from resolveurl.lib import helpers, jsunhunt
from resolveurl.resolver import ResolveUrl, ResolverError


class TubeLoadResolver(ResolveUrl):
    name = 'TubeLoad'
    domains = ['tubeload.co', 'redload.co']
    pattern = r'(?://|\.)((?:tube|red)load\.co)/(?:embed|e|f)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        headers.update({'Referer': web_url})
        if 'NOT FOUND' in html or 'Sorry' in html:
            raise ResolverError('File Removed')

        if jsunhunt.detect(html):
            html = re.findall('<head>(.*?)</head>', html, re.S)[0]
            html = jsunhunt.unhunt(html)

        aurl = 'https://{0}/assets/js/main.min.js'.format(host)
        ahtml = self.net.http_GET(aurl, headers=headers).content

        if jsunhunt.detect(ahtml):
            ahtml = jsunhunt.unhunt(ahtml)
            var, rep1, rep2 = re.findall(r'''var\s*res\s*=\s*([^.]+)\.replace\("([^"]+).+?replace\("([^"]+)''', ahtml, re.DOTALL)[0]
            r = re.search(r'var\s*{0}\s*=\s*"([^"]+)'.format(var), html)
            if r:
                surl = r.group(1).replace(rep1, '')
                surl = surl.replace(rep2, '')
                surl = helpers.b64decode(surl)
                headers.update({'verifypeer': 'false'})
                return surl.replace(' ', '%20') + helpers.append_headers(headers)

        raise ResolverError("Video not found")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
