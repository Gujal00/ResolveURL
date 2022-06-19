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
import json
import base64
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamRapidResolver(ResolveUrl):
    name = 'StreamRapid'
    domains = ['streamrapid.ru', 'rabbitstream.net']
    pattern = r'(?://|\.)((?:rabbitstream|streamrapid)\.(?:ru|net))/embed-([^\n]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            # Needs to be hard coded for now if nothing is passed in.
            referer = 'https://{0}/'.format(host)
        web_url = self.get_url(host, media_id)
        rurl = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        html = self.net.http_GET(web_url, headers).content
        domain = base64.b64encode((rurl[:-1] + ':443').encode('utf-8')).decode('utf-8').replace('=', '.')
        token = helpers.girc(html, rurl, domain)
        number = re.findall(r"recaptchaNumber\s*=\s*'(\d+)", html)
        if token and number:
            eid, media_id = media_id.split('/')
            headers.update({'Referer': web_url, 'Accept': '*/*'})
            surl = '{0}ajax/embed-{1}/getSources'.format(rurl, eid)
            if '?' in media_id:
                media_id = media_id.split('?')[0]
            data = {'_number': number[0],
                    'id': media_id,
                    '_token': token}
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            shtml = self.net.http_GET('{0}?{1}'.format(surl, urllib_parse.urlencode(data)), headers=headers).content
            sources = json.loads(shtml).get('sources')
            if sources:
                source = sources[0].get('file')
                headers.pop('X-Requested-With')
                headers.pop('Accept')
                headers.update({'Referer': rurl, 'Origin': rurl[:-1]})
                return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}')
