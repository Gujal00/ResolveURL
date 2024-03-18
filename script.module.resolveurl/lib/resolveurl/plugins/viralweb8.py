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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from six.moves import urllib_parse


class ViralWeb8Resolver(ResolveUrl):
    name = 'ViralWeb8'
    domains = ['viralweb8.com']
    pattern = r'(?://|\.)(viralweb8\.com)/video/([^\n]+)'

    def get_media_url(self, host, media_id, subs=False):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = None

        web_url = self.get_url(host, media_id)
        if referer is None:
            referer = urllib_parse.urljoin(web_url, '/')

        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        response = self.net.http_GET(web_url, headers=headers).content
        response = helpers.get_packed_data(response)
        if subs:
            subtitles = helpers.scrape_subtitles(response, web_url)

        data_url = self.get_dataurl(host, media_id)
        data = {'hash': media_id, 'r': referer}
        headers.pop('Referer')
        headers.update({
            'Origin': 'https://{0}'.format(host),
            'X-Requested-With': 'XMLHttpRequest'
        })
        resp = self.net.http_POST(data_url, form_data=data, headers=headers).content
        resp = json.loads(resp)

        src = resp.get('securedLink')
        if src:
            headers = {'User-Agent': common.FF_USER_AGENT}
            stream_url = src + helpers.append_headers(headers)
            if subs:
                return stream_url, subtitles
            return stream_url

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/video/{media_id}')

    def get_dataurl(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/index.php?data={media_id}&do=getVideo')
