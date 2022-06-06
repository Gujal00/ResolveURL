"""
    Plugin for ResolveURL
    Copyright (C) 2011 t0mm0

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


class MailRuResolver(ResolveUrl):
    name = 'MailRu'
    domains = ['mail.ru', 'my.mail.ru', 'm.my.mail.ru', 'videoapi.my.mail.ru', 'api.video.mail.ru']
    # This pattern is starting to becoming unreliable and we may have to rethink it to support all the current urls
    pattern = r'(?://|\.)(mail\.ru)/(?:\w+/)?(?:videos/embed/)?(inbox|mail|embed|mailua|list|bk|v)/(?:([^/]+)/[^.]+/)?(\d+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        response = self.net.http_GET(web_url)
        html = response.content

        if html:
            try:
                js_data = json.loads(html)
                sources = [(video['key'], video['url']) for video in js_data['videos']]
                sorted(sources)
                source = helpers.pick_source(sources)
                source = source.encode('utf-8') if helpers.PY2 else source
                if source.startswith("//"):
                    source = 'http:%s' % source
                return source + helpers.append_headers({'Cookie': response.get_headers(as_dict=True).get('Set-Cookie', '')})
            except:
                raise ResolverError('No playable video found.')

        else:
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        location, user, media_id = media_id.split('|')
        if user == 'None':
            return 'http://my.mail.ru/+/video/meta/%s' % (media_id)
        else:
            return 'http://my.mail.ru/+/video/meta/%s/%s/%s?ver=0.2.60' % (location, user, media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return (r.group(1), '%s|%s|%s' % (r.group(2), r.group(3), r.group(4)))
        else:
            return False
