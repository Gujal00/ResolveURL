"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
import json
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class EmbedojoResolver(ResolveUrl):
    name = 'Embedojo'
    domains = ['embedojo.net', 'embedplayer1.xyz', 'llanfairpwllgwyngyll.com', 'llanfairpwllgwyngy.com']
    pattern = r'(?://|\.)((?:embed(?:ojo|player1)|llanfairpwllgwyngyl*)\.(?:net|xyz|com))/([0-9a-zA-Z$:/.-_]+)'

    def get_media_url(self, host, media_id, subs=False):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            ref = urllib_parse.urljoin(referer, '/')
        else:
            ref = False
        subtitles = {}
        web_url = self.get_url(host, media_id)
        if not ref:
            ref = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': ref}
        resp = self.net.http_GET(web_url, headers=headers)
        if web_url != resp.get_url():
            web_url = resp.get_url()
            ref = urllib_parse.urljoin(web_url, '/')
            headers.update({'Referer': ref})
        response = helpers.get_packed_data(resp.content)
        r = re.search(r'FirePlayer\("([^"]+)",\s*(.*?),\s*(?:true|false)', response, re.DOTALL)
        if r:
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': ref[:-1]
            })
            eurl = urllib_parse.urljoin(web_url, '/player/index.php?data={0}&do=getVideo'.format(r.group(1)))
            data = {'hash': r.group(1), 'r': ref}
            resp = self.net.http_POST(eurl, data, headers).content
            if resp:
                # src = json.loads(resp).get('securedLink')
                src = json.loads(resp)
                stream_url = src.get('videoSource') + helpers.append_headers(headers)
                headers.pop('X-Requested-With')
                if subs:
                    sdata = json.loads(r.group(2))
                    if sdata.get('tracks'):
                        for track in sdata.get('tracks'):
                            if track.get('kind') == 'captions':
                                subtitles.update({track.get('label'): track.get('file')})
                    return stream_url, subtitles
                return stream_url

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
