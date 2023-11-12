# -*- coding: utf-8 -*-
"""
    Plugin for ResolveURL
    Copyright (C) 2018 gujal

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
from resolveurl.lib import helpers, aadecode
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidBomResolver(ResolveUrl):
    name = 'VidBom'
    domains = ['vidbom.com', 'vidbem.com', 'vidbm.com', 'vedpom.com', 'vedbom.com', 'vedbom.org',
               'vedbam.xyz', 'myvid.com', 'vidshar.org', 'vedbam1.space', 'vedbam1.store',
               'vadbom.com', 'vidbam.org', 'vadbam.com', 'vadbam.net', 'myviid.com', 'myviid.net',
               'vidshare.com', 'vedsharr.com', 'vedshar.com', 'vedshare.com', 'vadshar.com',
               'viidshar.com', 'vedbam1.online', 'qaz2.vedbam1.online', 'vedbam1.sbs']
    pattern = r'(?://|\.)((?:v[aie]d[bp][aoe]?m|myvii?d|v[aei]*dshar[er]?)\d*\.' \
              r'(?:com|net|org|xyz|online|sbs|space|store))(?::\d+)?/(?:embed[/-])?([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        html = html.encode('utf-8') if helpers.PY2 else html
        aa_text = re.search(r"""(ﾟωﾟﾉ\s*=\s*/｀ｍ´\s*）\s*ﾉ.+?;)\s*</script""", html, re.I)

        if aa_text:
            aa_decoded = aadecode.decode(aa_text.group(1))
            sources = helpers.scrape_sources(aa_decoded)
        else:
            sources = helpers.scrape_sources(html, patterns=[r'''sources:\s*\[{(?:src|file):\s*"(?P<url>[^"]+)'''])

        if sources:
            headers.update({'Referer': web_url})
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}.html')
