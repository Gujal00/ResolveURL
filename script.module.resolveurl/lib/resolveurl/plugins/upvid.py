# -*- coding: utf-8 -*-
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

import re
from resolveurl import common
from resolveurl.lib import helpers, aadecode
from resolveurl.resolver import ResolveUrl, ResolverError


class UpVidResolver(ResolveUrl):
    name = 'UpVid'
    domains = ['upvid.co', 'upvid.pro', 'upvid.live', 'upvid.host', 'upvid.biz', 'upvid.cloud',
               'opvid.org', 'opvid.online', 'turbovid.org', 'turbovid.co']
    pattern = r'(?://|\.)((?:up|op|turbo)vid\.(?:co|org|pro|live|host|biz|cloud|online))/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        iframe = True
        url = web_url
        while iframe:
            html = self.net.http_GET(url, headers=headers).content
            headers.update({'Referer': web_url})
            i = re.search(r'id="link"\s*value="([^"]+)', html) or re.search(r'<iframe.+src="([^"]+)', html)
            if i:
                url = i.group(1).replace('\n', '')
            else:
                iframe = False

        r = re.search(r'value="([^"]+)"\s*id="func"', html)
        if r:
            html = html.encode('utf-8') if helpers.PY2 else html
            aa_text = re.search(r"""(ﾟωﾟﾉ\s*=\s*/｀ｍ´\s*）\s*ﾉ.+?;)\s*(?:var|</script)""", html, re.I)
            if aa_text:
                aa_text = aadecode.decode(aa_text.group(1))
            key = re.search(r"func\.inner[^(]+\('([^']+)", aa_text)
            if key:
                shtml = helpers.arc4(key.group(1), r.group(1))
                src = re.search(r"'src',\s*'([^']+)", shtml)
                if src:
                    return src.group(1) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
