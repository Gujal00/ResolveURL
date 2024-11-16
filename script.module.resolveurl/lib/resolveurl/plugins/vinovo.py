"""
    Plugin for ResolveURL
    Copyright (C) 2024 gujal

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

import json
import re
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VinovoResolver(ResolveUrl):
    name = 'Vinovo'
    domains = ['vinovo.to', 'vinovo.si']
    pattern = r'(?://|\.)(vinovo\.(?:to|si))/(?:e|d)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        t = re.search(r'name="token"\s*content="([^"]+)', html)
        s = re.search(r'<video.+?data-base="([^"]+)', html)
        if subs:
            subtitles = {}
            su = re.search(r'<track.+?src="([^"]+)"\s*srclang="([^"]+)', html)
            if su:
                subtitles.update({su.group(2): su.group(1)})
        if t and s:
            rurl = urllib_parse.urljoin(web_url, '/')
            recaptcha = helpers.girc(html, rurl)
            headers.update({
                'Origin': rurl[:-1],
                'Referer': rurl,
                'X-Requested-With': 'XMLHttpRequest'
            })
            payload = {
                'token': t.group(1),
                'recaptcha': recaptcha
            }
            api_url = 'https://vinovo.to/api/file/url/{0}'.format(media_id)
            resp = self.net.http_POST(api_url, form_data=payload, headers=headers).content
            resp = json.loads(resp)
            if resp.get('status') == 'ok':
                headers.pop('X-Requested-With')
                vid_src = '{0}/stream/{1}'.format(s.group(1), resp.get('token')) + helpers.append_headers(headers)
                if subs:
                    return vid_src, subtitles
                return vid_src

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vinovo.to/e/{media_id}')
