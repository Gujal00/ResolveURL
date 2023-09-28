"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from six.moves import urllib_error


class StreamTapeResolver(ResolveUrl):
    name = 'StreamTape'
    domains = ['streamtape.com', 'strtape.cloud', 'streamtape.net', 'streamta.pe', 'streamtape.site',
               'strcloud.link', 'strtpe.link', 'streamtape.cc', 'scloud.online', 'stape.fun',
               'streamadblockplus.com', 'shavetape.cash', 'streamtape.to', 'streamta.site',
               'streamadblocker.xyz', 'tapewithadblock.org', 'adblocktape.wiki', 'antiadtape.com',
               'streamtape.xyz', 'tapeblocker.com']
    pattern = r'(?://|\.)(' \
              r'(?:s(?:tr)?(?:eam|have)?|tapewith)?(?:adblock(?:er|plus)?|antiad)?(?:ta?p?e?|cloud)?' \
              r'(?:blocker)?\.' \
              r'(?:com|cloud|net|pe|site|link|cc|online|fun|cash|to|xyz|org|wiki)' \
              r')/(?:e|v)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': 'https://{0}/'.format(host)
        }
        try:
            r = self.net.http_GET(web_url, headers=headers).content
        except urllib_error.HTTPError as e:
            if e.code == 503:
                raise ResolverError('Site using Cloudflare DDOS protection')
            else:
                raise ResolverError('Video deleted or removed.')
            return
        src = re.findall(r'''ById\('.+?=\s*(["']//[^;<]+)''', r)
        if src:
            src_url = ''
            parts = src[-1].replace("'", '"').split('+')
            for part in parts:
                p1 = re.findall(r'"([^"]*)', part)[0]
                p2 = 0
                if 'substring' in part:
                    subs = re.findall(r'substring\((\d+)', part)
                    for sub in subs:
                        p2 += int(sub)
                src_url += p1[p2:]
            src_url += '&stream=1'
            src_url = 'https:' + src_url if src_url.startswith('//') else src_url
            return helpers.get_redirect_url(src_url, headers) + helpers.append_headers(headers)
        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
