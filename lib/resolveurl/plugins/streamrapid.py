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

from six.moves import urllib_parse
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import re
import json


class StreamRapidResolver(ResolveUrl):
    name = "streamrapid"
    domains = ['streamrapid.ru']
    pattern = r'(?://|\.)(streamrapid\.ru)/embed-([^\n]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        web_url = self.get_url(host, media_id)
        rurl = urllib_parse.urljoin(web_url, '/')
        if not referer:
            referer = rurl
        domain = 'aHR0cHM6Ly9zdHJlYW1yYXBpZC5ydTo0NDM.'
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        html = self.net.http_GET(web_url, headers).content
        token = helpers.girc(html, rurl, domain)
        number = re.findall(r"recaptchaNumber\s*=\s*'(\d+)", html)
        if token and number:
            eid, media_id = media_id.split('/')
            surl = 'https://streamrapid.ru/ajax/embed-{0}/getSources'.format(eid)
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
                return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}')
