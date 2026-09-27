"""
    Plugin for ResolveURL
    Copyright (c) 2026 gujal

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class AnonMP4Resolver(ResolveUrl):
    name = 'AnonMP4'
    domains = ['anonmp4.help', 'anonmp4.art']
    pattern = r'(?://|\.)(anonmp4\.(?:help|art))/embed/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content

        play_seed = re.search(r'PLAY_SEED\s*=\s*[\'"]([^\'"]+)', html)
        play_sig = re.search(r'PLAY_SIG\s*=\s*[\'"]([^\'"]+)', html)

        if play_seed and play_sig:
            ref = urllib_parse.urljoin(web_url, '/')
            api_url = urllib_parse.urljoin(web_url, '/video-api')
            post_headers = headers.copy()
            post_headers.update({
                'Referer': web_url,
                'Origin': ref[:-1],
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            })
            payload = {
                'ticket': play_seed.group(1),
                'sig': play_sig.group(1)
            }
            r = self.net.http_POST(api_url, form_data=payload, headers=post_headers, jdata=True).json
            if r.get('error'):
                raise ResolverError(r.get('error'))

            if 'tracks' in r.keys():
                tracks = [(x.get('track_name'), x.get('track_url')) for x in r.get('tracks')]
                surl = helpers.pick_source(tracks, auto_pick=False)
                r = self.net.http_GET(surl, headers=headers).json

            if 'hls' in r.keys():
                url = r.get('hls') + helpers.append_headers(headers)
                if subs:
                    subtitles = {}
                    s = r.get('subtitles')
                    if s:
                        subtitles = {x.get('language'): x.get('url') for x in s}
                    return url, subtitles
                return url

        # Fallback to legacy GET method
        a = re.search(r"res\s*=\s*await\s*fetch\('([^']+)", html)
        if a:
            ref = urllib_parse.urljoin(web_url, '/')
            api_url = urllib_parse.urljoin(web_url, a.group(1))
            headers.update({'Referer': ref, 'Origin': ref[:-1]})
            r = self.net.http_GET(api_url, headers=headers).json
            if 'tracks' in r.keys():
                tracks = [(x.get('track_name'), x.get('track_url')) for x in r.get('tracks')]
                surl = helpers.pick_source(tracks, auto_pick=False)
                r = self.net.http_GET(surl, headers=headers).json

            if 'hls' in r.keys():
                url = r.get('hls') + helpers.append_headers(headers)
                if subs:
                    subtitles = {}
                    s = r.get('subtitles')
                    if s:
                        subtitles = {x.get('language'): x.get('url') for x in s}
                    return url, subtitles
                return url
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')
