"""
    resolveurl XBMC Addon
    Copyright (C) 2016 jsergio

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
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VidCloudResolver(ResolveUrl):
    name = 'vidcloud'
    domains = ['vidcloud.co', 'loadvid.online', 'vcstream.to']
    pattern = '(?://|\.)((?:vidcloud\.co|loadvid\.online|vcstream\.to))/(?:embed/|v/|player\?fid=)([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT, 'Referer': 'https://vidcloud.co/embed/%s' % media_id}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            sources = helpers.scrape_sources(html.replace("\\n", "").replace("\\", ""), patterns=[
                '''file":\s*"(?P<url>[^"]+)''', '''src":\s*"(?P<url>[^"]+)(?:[^}>\]]+)label":\s*"(?P<label>[^"]+)'''],
                                             generic_patterns=False)
            if sources:
                return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError("Unable to locate video")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidcloud.co/player?fid={media_id}&page=embed')
