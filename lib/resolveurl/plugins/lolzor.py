"""
grifthost resolveurl plugin
Copyright (C) 2015 tknorris

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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class LolzorResolver(ResolveUrl):
    name = "lolzor"
    domains = ["lolzor.com", "mycollection.net", "adhqmedia.com", "gagomatic.com", "funblr.com", "favour.me",
               "vidbaba.com", "likeafool.com"]
    pattern = '(?://|\.)((?:(?:lolzor|adhqmedia|gagomatic|funblr|vidbaba|likeafool)\.com|mycollection\.net|favour\.me))/([^/]+/embed/(?:\d+/)?[0-9a-zA-Z\-]+)'
    pattern2 = '(?://|\.)((?:(?:lolzor|adhqmedia|gagomatic|funblr|vidbaba|likeafool)\.com|mycollection\.net|favour\.me))/(video/\d+/[0-9a-zA-Z\-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            sources = helpers.parse_sources_list(html)
            if sources:
                return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File Not Found')

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url, re.I)
        r = r if r else re.search(self.pattern2, url, re.I)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        if isinstance(host, basestring):
            host = host.lower()

        if url:
            return re.search(self.pattern, url, re.I) is not None or re.search(self.pattern2, url, re.I) is not None
        else:
            return any(host in domain.lower() for domain in self.domains)

    def get_url(self, host, media_id):
        media_id = re.sub('video/(\d+)', r'video/embed/\1', media_id)
        return self._default_get_url(host, media_id, template='http://www.{host}/{media_id}')
